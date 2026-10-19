"""Base entity for the TEC heat pump."""

from __future__ import annotations

from typing import Any

from homeassistant.const import EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, TecDp
from .coordinator import TecCoordinator


class TecEntity(CoordinatorEntity[TecCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: TecCoordinator, desc: TecDp) -> None:
        super().__init__(coordinator)
        self.desc = desc
        self._attr_unique_id = f"{coordinator.device_id}_{desc.key}"
        self._attr_translation_key = desc.key
        self._attr_icon = desc.icon
        self._attr_device_class = desc.device_class
        self._attr_entity_registry_enabled_default = desc.enabled_default
        if desc.diagnostic:
            self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.device_id)},
            name="TEC heat pump",
            manufacturer="TEC",
            model="RS07",
        )

    @property
    def raw(self) -> Any:
        return (self.coordinator.data or {}).get(self.desc.dp)

    @property
    def available(self) -> bool:
        return super().available and self.raw is not None

    @property
    def scaled(self) -> Any:
        raw = self.raw
        if raw is None or isinstance(raw, (bool, str)) or self.desc.scale == 1:
            return raw
        return raw / self.desc.scale
