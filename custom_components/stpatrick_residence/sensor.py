"""Sensor Entity for St-Patrick Residence."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import MenuDataUpdateCoordinator


SENSOR_TYPES = {
    "lunch_main": SensorEntityDescription(
        key="lunch_main",
        icon="mdi:hamburger",
    ),
    "lunch_dessert": SensorEntityDescription(
        key="lunch_main",
        icon="mdi:cookie",
    ),
    "dinner_appetizer": SensorEntityDescription(
        key="appetizer",
        icon="mdi:pot-mix",
    ),
    "dinner_main": SensorEntityDescription(
        key="dinner_main",
        icon="mdi:pasta",
    ),
    "dinner_dessert": SensorEntityDescription(
        key="dinner_main",
        icon="mdi:cupcake",
    ),
}


class MealItemSensor(CoordinatorEntity, SensorEntity):
    """Representation of a meal item."""

    _domain = "sensor"

    def __init__(
        self,
        coordinator: MenuDataUpdateCoordinator,
        key: str,
    ) -> None:
        """Initialize the Mug sensor."""
        self.entity_description = SENSOR_TYPES[key]
        self.meal_type, self.item_type = key.split("_", 1)
        super().__init__(coordinator)

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
