class FakeGenerator:
    """In-memory TextGenerator capturing the arguments it was called with."""

    def __init__(
        self,
        model: str = "fake-model",
        text: str = "Plain explanation.",
        error: Exception | None = None,
    ) -> None:
        self.model = model
        self.text = text
        self.error = error
        self.instructions: str | None = None
        self.input_text: str | None = None

    async def generate(self, instructions: str, text: str) -> str:
        self.instructions = instructions
        self.input_text = text
        if self.error is not None:
            raise self.error
        return self.text
