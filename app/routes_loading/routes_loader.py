from .singleton_decorator import singleton
from .route_info import RouteInfo, DirectionInfo


@singleton
class Routes:
    """
    A class for managing the routes.
    Only one instance of the class can exist throughout the application.
    """

    def __init__(self):
        self.__routes = []

    def load_routes(self, routes_path: str) -> None:
        """
        Loads list of routes from the specified path.
        :param:
            routes_path: The path to the routes.txt file.
        """
        with open(routes_path, "rb") as f:
            try:
                self.__routes = self.parse_routes(f.read().decode("utf-8").splitlines())
                print("Routes was loaded")
            except ValueError:
                print("Error while loading routes")

    def parse_routes(self, lines: list[str]) -> list[RouteInfo]:
        routes = []
        current_route_number = None
        current_directions = []

        lines_iter = iter(lines)

        for line in lines_iter:
            line = line.strip()
            if not line:
                continue

            if line.startswith("|"):
                if current_route_number is not None and current_directions:
                    routes.append(RouteInfo(current_route_number, current_directions))
                    current_directions = []

                try:
                    next_line = next(lines_iter).strip()

                    if "#" in next_line:
                        next_line = next_line.split("#", 1)[0].strip()

                    if "-" in next_line:
                        next_line = next_line.replace("-", "").strip()

                    current_route_number = next_line if next_line else None

                    current_route_number = next_line
                except StopIteration:
                    print("Warning: Unexpected end of input after '|'")
                    current_route_number = None

            else:
                parts = line.split(",")
                if len(parts) < 3 or len(parts) > 4:
                    print(
                        f"Warning: Invalid line format (strange number of parts): {line}"
                    )
                    continue

                direction_id = parts[0].strip()
                point_id = parts[1].strip()
                full_names = parts[2]
                full_names = full_names.strip().replace("^", "-")

                short_names = None
                if len(parts) == 4:
                    short_names = parts[3]
                    short_names = short_names.strip().replace("^", "-")

                current_directions.append(
                    DirectionInfo(direction_id, point_id, full_names, short_names)  # type: ignore
                )

        if current_route_number is not None and current_directions:
            routes.append(RouteInfo(current_route_number, current_directions))

        return routes

    @property
    def routes(self):
        return self.__routes
