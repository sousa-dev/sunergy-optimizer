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

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the sunergy_optimizer component."""

    async def fetch_historical_data(entity_id, start_time, end_time=None):
        """Fetch historical data for an entity from Home Assistant's REST API."""
        headers = {
            "Authorization": f'Bearer {ACCESS_TOKEN}',
            "Content-Type": "application/json",
        }

        # Construct the URL for the history API endpoint
        start_time_str = start_time.isoformat()
        url = f"{HA_URL}/api/history/period/{start_time_str}"
        if end_time:
            end_time_str = end_time.isoformat()
            url += f"?end_time={end_time_str}"
        url += f"&filter_entity_id={entity_id}"

        # Log the url
        _LOGGER.info(f"Fetching historical data from {url}")

        session = async_get_clientsession(hass)
        async with session.get(url, headers=headers) as response:
            _LOGGER.info(response.status)
            if response.status == 200:
                history_data = await response.json()
                return history_data
            else:
                return None

    async def calc_total_energy_generated(start_time, end_time):
        """Calculate the total solar PV generation in the last week and day."""
        entity_id = 'input_number.solar_pv_generation'
        history_data = await fetch_historical_data(entity_id, start_time, end_time)
        if not history_data:
            return 'N/A', 'N/A'  # No data or an error occurred

        # Placeholder for actual calculation logic
        # You will need to process history_data to calculate the totals
        total_generation_last_week = 'Fetch'
        total_generation_last_day = 'Fetched'
            

        return total_generation_last_week, total_generation_last_day

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
        now = datetime.datetime.now()
        total_generation_last_week, total_generation_last_day = await calc_total_energy_generated(now - datetime.timedelta(days=15), now)
        hass.states.async_set(
            f'{DOMAIN}.Hello_World',
            f'Total Energy from Last day: {total_generation_last_day} vs Last week: {total_generation_last_week} | Updated at: {now}'
        )

    hass.async_create_task(initial_update())
    async_track_time_interval(hass, update_state, datetime.timedelta(minutes=1))

    return True
