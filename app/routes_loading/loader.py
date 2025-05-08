from .singleton_meta import SingletonMeta


class Routes(metaclass=SingletonMeta):
    """
    A class for managing the routes.
    Only one instance of the class can exist throughout the application.
    """

    def __init__(self):
        self.__routes = None

    def load_routes(self, routes_path: str) -> None:
        """
        Loads list of routes from the specified path.
        :param:
            routes_path: The path to the routes.txt file.
        """
        # with open(public_key_path, "rb") as f:
        #     try:
        #         self.__public_key = serialization.load_pem_public_key(f.read())
        #         print("Public key was loaded")
        #     except ValueError:
        #         print("Wrong file")
        pass

    def get_routes(self):
        return self.__routes
