"""Local Tuya connection for the TEC heat pump.

tinytuya is synchronous, so one dedicated thread owns a persistent socket. It
listens for DP updates that the device pushes, requests a full status every
STATUS_INTERVAL seconds, and sends queued writes. Updates are handed to the
event loop through the DataUpdateCoordinator.
"""

from __future__ import annotations

from datetime import timedelta
import logging
import queue
import threading
import time
from typing import Any

import tinytuya

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_DEVICE_ID,
    CONF_LOCAL_KEY,
    CONF_PROTOCOL_VERSION,
    DOMAIN,
    KNOWN_DPS,
    STALE_AFTER,
    STATUS_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

SOCKET_TIMEOUT = 5
MAX_BACKOFF = 60


def create_device(host: str, device_id: str, local_key: str, version: str) -> tinytuya.Device:
    """Create a tinytuya device (also used by the config flow)."""
    device = tinytuya.Device(device_id, host, local_key, version=float(version))
    device.set_socketTimeout(SOCKET_TIMEOUT)
    return device


class TecCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Holds the merged DP state (raw device values, keyed by DP number)."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, _LOGGER, config_entry=entry, name=DOMAIN)
        self._host: str = entry.data[CONF_HOST]
        self._device_id: str = entry.data[CONF_DEVICE_ID]
        self._local_key: str = entry.data[CONF_LOCAL_KEY]
        self._version: str = entry.data[CONF_PROTOCOL_VERSION]
        self._dps: dict[str, Any] = {}
        self._writes: queue.Queue[tuple[str, Any]] = queue.Queue()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._last_rx = time.monotonic()
        self._reported_unknown: set[str] = set()
        self._unsub_stale = None

    @property
    def device_id(self) -> str:
        return self._device_id

    # --- lifecycle (event loop) ---------------------------------------------

    async def async_start(self) -> None:
        self._thread = threading.Thread(
            target=self._run, name=f"{DOMAIN}-{self._device_id}", daemon=True
        )
        self._thread.start()
        self._unsub_stale = async_track_time_interval(
            self.hass, self._check_stale, timedelta(seconds=30)
        )

    async def async_stop(self) -> None:
        if self._unsub_stale:
            self._unsub_stale()
        self._stop.set()
        if self._thread:
            await self.hass.async_add_executor_job(self._thread.join, SOCKET_TIMEOUT * 2)

    async def async_set_dp(self, dp: str, value: Any) -> None:
        """Queue a write of a raw DP value and update the cache optimistically."""
        self._writes.put((dp, value))
        self._dps[dp] = value
        self.async_set_updated_data(dict(self._dps))

    @callback
    def _check_stale(self, _now) -> None:
        if self.last_update_success and time.monotonic() - self._last_rx > STALE_AFTER:
            self.async_set_update_error(
                UpdateFailed(f"No data from heat pump for {STALE_AFTER}s")
            )

    @callback
    def _apply(self, dps: dict[str, Any]) -> None:
        self._dps.update(dps)
        self.async_set_updated_data(dict(self._dps))

    # --- worker thread ------------------------------------------------------

    def _run(self) -> None:
        backoff = 1
        while not self._stop.is_set():
            device = create_device(self._host, self._device_id, self._local_key, self._version)
            device.set_socketPersistent(True)
            try:
                self._session(device)
                backoff = 1
            except Exception as err:  # noqa: BLE001 - keep the thread alive
                _LOGGER.warning("Heat pump connection error: %s", err)
            finally:
                try:
                    device.close()
                except Exception:  # noqa: BLE001
                    pass
            if not self._stop.is_set():
                _LOGGER.debug("Reconnecting in %ss", backoff)
                self._stop.wait(backoff)
                backoff = min(backoff * 2, MAX_BACKOFF)

    def _session(self, device: tinytuya.Device) -> None:
        """Run one connection until it fails or we are stopped."""
        self._handle(device.status())
        last_status = time.monotonic()
        _LOGGER.info("Connected to heat pump at %s", self._host)
        while not self._stop.is_set():
            while not self._writes.empty():
                dp, value = self._writes.get_nowait()
                _LOGGER.info("Writing DP %s = %s", dp, value)
                self._handle(device.set_value(int(dp), value))
            if time.monotonic() - last_status > STATUS_INTERVAL:
                self._handle(device.status())
                last_status = time.monotonic()
            msg = device.receive()  # returns None after SOCKET_TIMEOUT without data
            if msg is not None:
                self._handle(msg)

    def _handle(self, msg: dict | None) -> None:
        if not msg:
            return
        if "Err" in msg or "Error" in msg:
            raise ConnectionError(f"{msg.get('Err')}: {msg.get('Error')}")
        dps = msg.get("dps")
        if not dps:
            return
        self._last_rx = time.monotonic()
        for dp in dps.keys() - KNOWN_DPS - self._reported_unknown:
            _LOGGER.info("Unknown DP %s = %r", dp, dps[dp])
            self._reported_unknown.add(dp)
        _LOGGER.debug("DPs: %s", dps)
        self.hass.loop.call_soon_threadsafe(self._apply, dps)
