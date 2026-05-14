"""Sensor Entity for St-Patrick Residence."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import MenuUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback



SENSOR_TYPES = {
    "lunch_choice_1": SensorEntityDescription(
        key="lunch_choice_1",
        icon="mdi:hamburger",
    ),
    "lunch_choice_2": SensorEntityDescription(
        key="lunch_choice_2",
        icon="mdi:hamburger",
    ),
    "lunch_dessert": SensorEntityDescription(
        key="lunch_dessert",
        icon="mdi:cookie",
    ),
    "dinner_appetizer": SensorEntityDescription(
        key="appetizer",
        icon="mdi:pot-mix",
    ),
    "dinner_choice_1": SensorEntityDescription(
        key="dinner_choice_1",
        icon="mdi:pasta",
    ),
    "dinner_choice_2": SensorEntityDescription(
        key="dinner_choice_2",
        icon="mdi:pasta",
    ),
    "dinner_dessert": SensorEntityDescription(
        key="dinner_main",
        icon="mdi:cupcake",
    ),
}


class MealItemSensor(CoordinatorEntity[MenuUpdateCoordinator], SensorEntity):
    """Representation of a meal item."""

    _domain = "sensor"

    def __init__(
        self,
        coordinator: MenuUpdateCoordinator,
        key: str,
    ) -> None:
        """Initialize the Mug sensor."""
        super().__init__(coordinator)
        self.entity_description = SENSOR_TYPES[key]

        self.meal_type, self.item_type = key.split("_", 1)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{self.meal_type}_{self.item_type}"
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
        )

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if data := self.coordinator.data:
            return data.get(self.meal_type, {}).get(self.item_type)
        return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Entities."""
    if entry.entry_id is None:
        raise ValueError("Missing config entry ID")

    coordinator = entry.runtime_data
    async_add_entities([
        MealItemSensor(coordinator, key) for key in SENSOR_TYPES
    ])
