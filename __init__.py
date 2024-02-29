from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.event import async_track_time_interval
import datetime

DOMAIN = "sunergy_optimizer"

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the sunergy_optimizer component."""

    async def calc_total_energy_generated(start_time, end_time):
        return 'N/A', 'N/A'

    async def update_state(now):
        """Update the state every minute and query history."""
        end_time = now
        start_time = now - datetime.timedelta(days=15)  

        total_generation_last_week, total_generation_last_day = await calc_total_energy_generated(start_time, end_time)
        
        hass.states.async_set(
            'sunergy_optimizer.Hello_World',
            f'Total Energy from Last day: {total_generation_last_day} vs Last week: {total_generation_last_week} | Updated at: {now}'
        )

    async def initial_update():
        now = datetime.datetime.now()
        total_generation_last_week, total_generation_last_day = await calc_total_energy_generated(now - datetime.timedelta(days=15), now)
        hass.states.async_set(
            'sunergy_optimizer.Hello_World',
            f'Total Energy from Last day: {total_generation_last_day} vs Last week: {total_generation_last_week} | Updated at: {now}'
        )

    hass.async_create_task(initial_update())
    async_track_time_interval(hass, update_state, datetime.timedelta(minutes=1))

    return True
