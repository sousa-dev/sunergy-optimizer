import logging
import datetime
import asyncio

if __name__ == "__main__":
    from const import DOMAIN, HEADERS, TIME_INTERVAL
    from utils import get_fetch_url, calc_total_energy_generated
    from model import PVForecaster
else:
    from .const import DOMAIN, HEADERS, TIME_INTERVAL
    from .utils import get_fetch_url, calc_total_energy_generated
    from .model import PVForecaster

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

async def initialize(history_data):
    now = datetime.datetime.now()
    now = now.astimezone(datetime.timezone(datetime.timedelta(hours=-1)))

    model = PVForecaster()
    model.load_data(history_data)
    model.preprocess_data()
    model.train()

    prediction = model.predict()

    total_generation_last_week, total_generation_last_day = await calc_total_energy_generated(history_data)
    
    return f'{DOMAIN}.Hello_World', f'Prediction for the next 15min: {prediction} | Total Energy from Last day: {total_generation_last_day} vs Last week: {total_generation_last_week} | Initiated at: {now}'

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the sunergy_optimizer component."""

    async def fetch_historical_data(entity_id, end_time=datetime.datetime.fromisoformat(str(datetime.datetime.now()).replace('Z', '+00:00')), time_delta=TIME_INTERVAL):
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
        # Convert to Azores Timezone
        now = datetime.datetime.now().astimezone(datetime.timezone(datetime.timedelta(hours=-1)))

        history_data = await fetch_historical_data('input_number.solar_pv_generation')

        model = PVForecaster()
        model.load_data(history_data)
        model.preprocess_data()
        model.train()

        prediction = model.predict()

        evaluation = model.evaluate()

        actual_generation = model.data_15min.iloc[-1]['y']

        total_generation_last_week, total_generation_last_day = await calc_total_energy_generated(history_data)

        hass.states.async_set(f"{DOMAIN}.prediction", prediction, attributes={"unit_of_measurement": "kW", "friendly_name": "PV Prediction for next 15 minutes"})
        hass.states.async_set(f"{DOMAIN}.generated_pv_15min", actual_generation, attributes={"unit_of_measurement": "kWh", "friendly_name": "Total Generation in last 15 minutes"})
        hass.states.async_set(f"{DOMAIN}.total_generation_last_day", total_generation_last_day, attributes={"unit_of_measurement": "kWh", "friendly_name": "Total Generation Last Day"})
        hass.states.async_set(f"{DOMAIN}.total_generation_last_week", total_generation_last_week, attributes={"unit_of_measurement": "kWh", "friendly_name": "Total Generation Last Week"})

        
        # Set the state to the primary prediction value
        hass.states.async_set(
            f'{DOMAIN}.solar_generation_prediction', prediction,
            attributes={
                "total_energy_last_day": total_generation_last_day,
                "total_energy_last_week": total_generation_last_week,
                "last_update": now.isoformat()
            }
        )
        next_update = now + datetime.timedelta(minutes=TIME_INTERVAL)
        next_update.replace(second=0, microsecond=0)
        hass.states.async_set(f'{DOMAIN}.Hello_World', f'Prediction for the next 15min: {prediction} | Evaluation: {evaluation} |  Last update: {now}')


    async def initial_update(first_update=0):
        """Initial update to set the state."""
        history_data = await fetch_historical_data('input_number.solar_pv_generation')

        entity, update = await initialize(history_data)
        hass.states.async_set(entity, update + f" | First update at {first_update}")

    # Calculate time left for HH:00; HH:15; HH:30; HH:45
    # Azores Timezone
    now = datetime.datetime.now().astimezone(datetime.timezone(datetime.timedelta(hours=-1)))
    minutes_left = TIME_INTERVAL - (now.minute % TIME_INTERVAL)
    if minutes_left == TIME_INTERVAL:
        minutes_left = 0
    _LOGGER.info(f"First update scheduled in {minutes_left}")

    first_update = now + datetime.timedelta(minutes=minutes_left)
    first_update.replace(second=0, microsecond=0)
    hass.async_create_task(initial_update(first_update=now + datetime.timedelta(minutes=TIME_INTERVAL))) #TODO: Fix this

    async_track_time_interval(hass, update_state, datetime.timedelta(minutes=1))

    return True

async def main():
    """Main entry point of the sunergy_optimizer integration."""
    import aiohttp
    url = await get_fetch_url('input_number.solar_pv_generation')
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS) as response:
            if response.status == 200:
                history_data = await response.json()
                print(await initialize(history_data))
                return history_data
            else:
                print(f"Failed to fetch historical data. Status code: {response.status}. {response.text}")
                return None

if __name__ == "__main__":
    asyncio.run(main())
