import asyncio
import aiohttp

from pyipma.api import IPMA_API
from pyipma.location import Location

async def fetch_ipma_api_data(lon, lat):
    async with aiohttp.ClientSession() as session:
        api = IPMA_API(session)

        location = await Location.get(api, lon, lat, sea_stations=True)
        forecasts = await location.forecast(api, 1)    
        
        return {
            'current_hour': forecasts[0],
            'next_hour': forecasts[1]
        }

def get_weather_data(hass, entity_id = 'weather.ponta_delgada', domain = 'weather'):
    state = hass.states.get(entity_id)
    if state is None:
        return None
    
    # Access specific attributes
    print(state)
    temperature = state.attributes.get('temperature')
    humidity = state.attributes.get('humidity')
    condition = state.state  # The overall weather condition

    return {
        'temperature': temperature,
        'humidity': humidity,
        'condition': condition
    }

'''
Weather State Example

<state 

weather.ponta_delgada=rainy; temperature=17.4, temperature_unit=°C, humidity=97, pressure_unit=hPa, wind_bearing=SW, wind_speed=16.2, 
wind_speed_unit=km/h, visibility_unit=km, precipitation_unit=mm, 

forecast=[
    {'datetime': datetime.datetime(2024, 3, 14, 0, 0, tzinfo=datetime.timezone.utc), 
    'condition': 'rainy', 'precipitation_probability': 64.0, 'wind_bearing': 'SW', 'temperature': 18.3, 'templow': 15.5},

    {'datetime': datetime.datetime(2024, 3, 15, 0, 0, tzinfo=datetime.timezone.utc), 'condition': 'rainy', 'precipitation_probability': 92.0, 'wind_bearing': 'SW', 
    'temperature': 18.7, 'templow': 15.8}, {'datetime': datetime.datetime(2024, 3, 16, 0, 0, tzinfo=datetime.timezone.utc), 'condition': 'rainy', 
    'precipitation_probability': 83.0, 'wind_bearing': 'SW', 'temperature': 18.0, 'templow': 15.1}, 

    {'datetime': datetime.datetime(2024, 3, 17, 0, 0, tzinfo=datetime.timezone.utc), 'condition': 'partlycloudy', 'precipitation_probability': 48.0, 
    'wind_bearing': 'SW', 'temperature': 17.4, 'templow': 13.7}, {'datetime': datetime.datetime(2024, 3, 18, 0, 0, tzinfo=datetime.timezone.utc), 
    'condition': 'rainy', 'precipitation_probability': 96.0, 'wind_bearing': 'SW', 'temperature': 17.9, 'templow': 14.7}, 

    {'datetime': datetime.datetime(2024, 3, 19, 0, 0, tzinfo=datetime.timezone.utc), 'condition': 'rainy', 'precipitation_probability': 72.0, 'wind_bearing': 'NW', 
    'temperature': 16.6, 'templow': 12.9}, {'datetime': datetime.datetime(2024, 3, 20, 0, 0, tzinfo=datetime.timezone.utc), 'condition': 'partlycloudy', 
    'precipitation_probability': 14.0, 'wind_bearing': 'N', 'temperature': 16.3, 'templow': 13.1}, 
    
    {'datetime': datetime.datetime(2024, 3, 21, 0, 0, tzinfo=datetime.timezone.utc), 'condition': 'partlycloudy', 'precipitation_probability': 17.0, 
    'wind_bearing': 'NE', 'temperature': 17.1, 'templow': 13.5}, {'datetime': datetime.datetime(2024, 3, 22, 0, 0, tzinfo=datetime.timezone.utc),
    'condition': 'partlycloudy', 'precipitation_probability': 24.0, 'wind_bearing': 'NE', 'temperature': 17.4, 'templow': 13.8}
    ], 

attribution=Instituto Português do Mar e Atmosfera, 

friendly_name=Ponta Delgada,

supported_features=3 @ 2024-03-13T11:19:25.555488-01:00

>
'''
