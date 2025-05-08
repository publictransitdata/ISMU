class SingletonMeta(type):
    """
    A metaclass for implementing the Singleton pattern.
    Ensures that only one instance of a class exists throughout the application.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Returns the single shared instance of the class. If the instance
        does not exist yet, it creates one and stores it.
        :param:
            *args: Positional arguments for the class constructor.
            **kwargs: Keyword arguments for the class constructor.
        :return: Object: The single instance of the class.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
