from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.event import async_track_time_interval
import datetime

DOMAIN = "sunergy_optimizer"

def setup(hass: HomeAssistant, config: ConfigType) -> bool:
	"""Set up a skeleton component."""
	# States are in the format DOMAIN.OBJECT_ID.
	hass.states.set('sunergy_optimizer.Hello_World', 'Initiated at {}'.format(datetime.datetime.now()))

	# Return boolean to indicate that initialization was successfully!
	return True