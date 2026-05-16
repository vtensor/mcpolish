"""Discovery: server.add_tool(name=..., description=..., input_schema=...)."""


class Server:
    """Pretend server with an add_tool method. The discoverer only reads the
    source, so the implementation does not need to be real for the test."""

    def add_tool(self, **kwargs):
        return kwargs


server = Server()

server.add_tool(
    name="get_temperature",
    description=(
        "Use this when the user asks for the current temperature at a city. "
        "Returns a number in degrees Celsius."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "City name. Example: 'Paris'.",
                "example": "Paris",
            },
        },
        "required": ["city"],
    },
)
