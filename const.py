DOMAIN = "sunergy_optimizer"
HA_URL = 'http://127.0.0.1:8123'
ACCESS_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJmODk1ODkyNzFjYjk0NjdiODA3NDFlMzI4YjNhOTBhYyIsImlhdCI6MTcwOTg0ODcxMywiZXhwIjoyMDI1MjA4NzEzfQ.6n7f-cNctUE-IP9eFVa_fZ48seJ_i9xw8_Y7IqW8EqE'
HEADERS = {
    "Authorization": f'Bearer {ACCESS_TOKEN}',
    "Content-Type": "application/json",
}

TIME_INTERVAL = 15

LOCATION = None 