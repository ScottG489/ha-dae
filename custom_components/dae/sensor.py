"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfLength, UnitOfVolume
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .client import MeterDevice
from .const import DOMAIN
from .coordinator import DaeDataUpdateCoordinator

UNIT_MAP = {
    "Gallon": UnitOfVolume.GALLONS,
}


class DaeSensor(CoordinatorEntity[DaeDataUpdateCoordinator], SensorEntity):
    """Representation of a DaeSensor."""

    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_device_class = SensorDeviceClass.WATER
    _attr_has_entity_name = True

    def __init__(
            self,
            meter_device: MeterDevice,
            coordinator: DaeDataUpdateCoordinator,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.meter_device = meter_device
        self._attr_unique_id = f"dae_meter_{str(meter_device.meter.channel_id)}".lower()
        self._attr_native_unit_of_measurement = UNIT_MAP[meter_device.meter.unit]

        self._attr_device_info = DeviceInfo(
            # TODO: Unique enough?
            identifiers={(DOMAIN, str(meter_device.meter.channel_id))},
            name=meter_device.channel.channel_name,
            manufacturer="DAE",
            model=meter_device.channel.model,
        )

    @property
    def native_value(self) -> int | None:
        """Return the meters value."""
        meter = self.coordinator.data[self.meter_device.meter.channel_id].meter
        self._attr_extra_state_attributes = {
            "disconnected": meter.disconnected
        }
        return meter.value


async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up dae sensors for config entries."""
    dae_coordinator: DaeDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]
    meter_devices = dae_coordinator.data

    async_add_entities(
        [
            DaeSensor(meter_device, dae_coordinator)
            for meter_device in meter_devices.values()
        ],
        True,
    )
