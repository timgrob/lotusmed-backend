from src.agents.agentic import AIProvider


class FakeAgent:
    """In-memory Agentic implementation capturing the arguments it was called with."""

    def __init__(
        self,
        provider: AIProvider = AIProvider.OPENAI,
        text: str = "Plain explanation.",
        error: Exception | None = None,
    ) -> None:
        self.provider = provider
        self.text = text
        self.error = error
        self.instructions: str | None = None
        self.input_text: str | None = None
        self.model_used: str | None = None

    async def generate(self, instructions: str, text: str, model: str) -> str:
        self.instructions = instructions
        self.input_text = text
        self.model_used = model
        if self.error is not None:
            raise self.error
        return self.text


class FakeRenderer:
    """In-memory Renderer capturing the HTML it was asked to render."""

    def __init__(
        self, image: bytes = b"png-bytes", error: Exception | None = None
    ) -> None:
        self.image = image
        self.error = error
        self.html: str | None = None

    async def render(self, html: str) -> bytes:
        self.html = html
        if self.error is not None:
            raise self.error
        return self.image
