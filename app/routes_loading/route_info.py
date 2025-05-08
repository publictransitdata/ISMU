class DirectionInfo:
    def __init__(
        self,
        group_id: str,
        point_id: str,
        full_names: str,
        short_names: None,
    ):
        self.group_id = group_id
        self.point_id = point_id
        self.full_names = full_names
        self.short_names = short_names


class RouteInfo:
    def __init__(self, route_number: str, directions: list[DirectionInfo]):
        self.route_number = route_number
        self.directions = directions
