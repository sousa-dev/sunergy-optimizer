from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import logging
import datetime

_LOGGER = logging.getLogger(__name__)

DOMAIN = "sunergy_optimizer"
HA_URL = 'http://127.0.0.1:8123'
ACCESS_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJmNTY4ZmNmYjA2N2Y0ZDMyODFmZGY2MjhjMGQ2NzZjZSIsImlhdCI6MTcwOTIyMDI1NiwiZXhwIjoyMDI0NTgwMjU2fQ.q5R6i0jkl0suA7fS4QMx5XAY8uo99zTydXUbhyrLHbY'

HEADERS = {
    "Authorization": f'Bearer {ACCESS_TOKEN}',
    "Content-Type": "application/json",
}

async def initialize(history_data):
    now = datetime.datetime.now()
    total_generation_last_week, total_generation_last_day = await calc_total_energy_generated(history_data)
    return f'{DOMAIN}.Hello_World', f'Total Energy from Last day: {total_generation_last_day} vs Last week: {total_generation_last_week} | Updated at: {now}'

async def get_fetch_url(entity_id, start_time=datetime.datetime.now() - datetime.timedelta(days=15), end_time=datetime.datetime.now()):
    """Fetch historical data for an entity from Home Assistant's REST API."""
    # Construct the URL for the history API endpoint
    start_time_str = start_time.isoformat().replace('+00:00', 'Z')
    url = f"{HA_URL}/api/history/period/{start_time_str}"
    if end_time:
        end_time_str = end_time.isoformat().replace('+00:00', 'Z')
        url += f"?end_time={end_time_str}"
    url += f"&filter_entity_id={entity_id}"

    return url

async def calc_total_energy_generated(history_data, end_time=datetime.datetime.now()):
    """Calculate the total solar PV generation in the last week and day."""

    if not history_data:
        return 'N/A', 'N/A'  # No data or an error occurred

    total_generation_last_week = 0
    total_generation_last_day = 0

    # Calculate total generation in the last week and last day
    for entry in history_data:
        for val in entry:
            value = val['state']
            _LOGGER.info(f"Value: {value}")
            # Remove the timezone information (+00:00) and microseconds (.666640) from the string
            last_changed_str = val['last_changed'].split('.')[0].replace('T', ' ')

            # Convert the string to a datetime object
            last_changed_datetime = datetime.datetime.strptime(last_changed_str, '%Y-%m-%d %H:%M:%S').astimezone(datetime.timezone.utc)

            # Convert the string to a datetime object
            end_time = datetime.datetime.fromisoformat(str(end_time).replace('Z', '+00:00'))
            
            # Convert the datetime object to UTC
            end_time = end_time.astimezone(datetime.timezone.utc)        # Calculate the total generation in the last week
            if last_changed_datetime > (end_time - datetime.timedelta(days=7)):
                total_generation_last_week += float(value) if value or value != '' else 0
            # Calculate the total generation in the last day
            if last_changed_datetime > (end_time - datetime.timedelta(days=1)):
                total_generation_last_day += float(value) if value or value != '' else 0
                

    return total_generation_last_week, total_generation_last_day


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the sunergy_optimizer component."""

    async def fetch_historical_data(entity_id, start_time=datetime.datetime.now(), time_delta=15):
        start_time = datetime.datetime.fromisoformat(str(start_time).replace('Z', '+00:00'))
        end_time = start_time - datetime.timedelta(minutes=time_delta)
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
        end_time = now
        start_time = now - datetime.timedelta(days=15)

        total_generation_last_week, total_generation_last_day = await calc_total_energy_generated(start_time, end_time)
        
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
    async_track_time_interval(hass, update_state, datetime.timedelta(minutes=15))

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
