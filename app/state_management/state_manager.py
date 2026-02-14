import os
import ujson as json
from utils.singleton_decorator import singleton
from app.error_codes import ErrorCodes
from utils.error_handler import set_error_and_raise

STATE_PATH = "app/state_management/state.json"
TEMP_STATE_PATH = "app/state_management/state.tmp"

@singleton
class StateManager:
    def __init__(self):
        self._state = {}

    def save_state(self, selected_route_id, selected_trip_id):
        try:
            rec = {
                "route_id": selected_route_id,
                "trip_id": selected_trip_id,
            }
            with open(TEMP_STATE_PATH, "w") as file:
                file.write(json.dumps(rec))
                file.flush()

            os.sync() 
            os.rename(TEMP_STATE_PATH, STATE_PATH)
            os.sync()

        except OSError:
            set_error_and_raise(ErrorCodes.TEMP_STATE_WRITE_ERROR)

    def get_state(self):
        state_info = self._load_state()
        if state_info is None:
            return {"route_id": 0, "trip_id": 0}
        return state_info

    def reset_state(self):
        self.save_state(0, 0)


    def _load_state(self) -> dict | None:
        try:
            with open(STATE_PATH, "r") as file:
                return json.loads(file.read())
        except OSError:
            pass

        try:
            with open(TEMP_STATE_PATH, "r") as file:
                return json.loads(file.read())
        except OSError:
            return None