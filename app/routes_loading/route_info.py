class DirectionInfo:
    def __init__(
        self,
        group_id: str,
        point_id: str,
        full_name: str,
        short_name: None,
    ):
        self.group_id = group_id
        self.point_id = point_id
        self.full_name = full_name
        self.short_name = short_name


class RouteInfo:
    def __init__(self, route_number: str, directions: list[DirectionInfo]):
        self.route_number = route_number
        self.directions = directions
