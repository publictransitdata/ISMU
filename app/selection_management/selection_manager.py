import os

import ujson as json

from app.error_codes import ErrorCodes
from utils.error_handler import set_error_and_raise
from utils.singleton_decorator import singleton

SELECTION_PATH = "app/selection_management/selection.json"
TEMP_SELECTION_PATH = "app/selection_management/selection.tmp"


@singleton
class SelectionManager:
    def __init__(self):
        self._selection = {}

    def save_selection(self, selected_route_id, selected_trip_id):
        try:
            rec = {
                "route_id": selected_route_id,
                "trip_id": selected_trip_id,
            }
            with open(TEMP_SELECTION_PATH, "w") as file:
                file.write(json.dumps(rec))
                file.flush()

            os.sync()
            os.rename(TEMP_SELECTION_PATH, SELECTION_PATH)
            os.sync()

        except OSError as err:
            set_error_and_raise(ErrorCodes.TEMP_SELECTION_WRITE_ERROR, err, show_message=True)

    def get_selection(self):
        selection_info = self._load_selection()
        if selection_info is None:
            return {"route_id": 0, "trip_id": 0}
        return selection_info

    def reset_selection(self):
        self.save_selection(0, 0)

    def _load_selection(self) -> dict | None:
        try:
            with open(SELECTION_PATH) as file:
                return json.loads(file.read())
        except OSError:
            pass

        try:
            with open(TEMP_SELECTION_PATH) as file:
                return json.loads(file.read())
        except OSError:
            return None
