import logging
import datetime

from .const import DOMAIN, HEADERS
from .utils import get_fetch_url, calc_total_energy_generated

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

async def initialize(history_data):
    now = datetime.datetime.now()
    total_generation_last_week, total_generation_last_day = await calc_total_energy_generated(history_data)
    return f'{DOMAIN}.Hello_World', f'Total Energy from Last day: {total_generation_last_day} vs Last week: {total_generation_last_week} | Initiated at: {now}'

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the sunergy_optimizer component."""

    async def fetch_historical_data(entity_id, end_time=datetime.datetime.fromisoformat(str(datetime.datetime.now()).replace('Z', '+00:00')), time_delta=15):
        start_time = end_time - datetime.timedelta(days=time_delta)

        url = await get_fetch_url(entity_id, start_time, end_time)

        # Log the url
        _LOGGER.info(f"Fetching historical data from {url}")

        session = async_get_clientsession(hass)
        async with session.get(url, headers=HEADERS) as response:
            if response.status == 200:
                history_data = await response.json()
                return history_data
            else:
                _LOGGER.error(f"Failed to fetch historical data for {entity_id}. Status code: {response.status}")
                return None
       
    async def update_state(now):
        """Update the state every minute and query history."""

        history_data = await fetch_historical_data('input_number.solar_pv_generation')

        total_generation_last_week, total_generation_last_day = await calc_total_energy_generated(history_data)
        
        hass.states.async_set(
            f'{DOMAIN}.Hello_World',
            f'Total Energy from Last day: {total_generation_last_day} vs Last week: {total_generation_last_week} | Updated at: {datetime.datetime.now()}'
        )

    async def initial_update():
        """Initial update to set the state."""
        history_data = await fetch_historical_data('input_number.solar_pv_generation')

        entity, update = await initialize(history_data)
        hass.states.async_set(entity, update)

    hass.async_create_task(initial_update())
    async_track_time_interval(hass, update_state, datetime.timedelta(minutes=1))

    return True

async def main():
    """Main entry point of the sunergy_optimizer integration."""
    import aiohttp
    url = await get_fetch_url('input_number.solar_pv_generation')
    print(url)
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS) as response:
            if response.status == 200:
                history_data = await response.json()
                print(await initialize(history_data))
                return history_data
            else:
                print(f"Failed to fetch historical data. Status code: {response.status}")
                return None

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
