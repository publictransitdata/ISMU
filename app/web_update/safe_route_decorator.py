def safe_route(server):
    """In case of an exception, return 500 without dumping the server."""

    def outer(fn):
        async def inner(request, *args, **kwargs):
            try:
                return await fn(request, *args, **kwargs)
            except Exception as e:
                return server._error_response(
                    "Internal server error: {}".format(e), 500, "text/plain"
                )

        return inner

    return outer
