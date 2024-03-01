import datetime
from .const import HA_URL

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
