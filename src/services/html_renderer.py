from typing import Protocol

from playwright.async_api import (
    Browser,
    Error as PlaywrightError,
    Playwright,
    async_playwright,
)

from src.core.exceptions import InfographicRenderError

# Width of a mobile phone viewport; the infographic prompt targets a single-column
# mobile layout, so the rendered image is a tall, narrow strip.
_VIEWPORT_WIDTH = 420


class Renderer(Protocol):
    """Turns a self-contained HTML document into a PNG image."""

    async def render(self, html: str) -> bytes: ...


class HtmlRenderer:
    """Render HTML to PNG with a single, process-long headless Chromium browser.

    The browser is launched once via ``start`` and reused across requests; each
    ``render`` runs in a fresh browser context for isolation.
    """

    def __init__(self) -> None:
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None

    async def start(self) -> None:
        """Launch the shared headless browser. Call once at application startup."""
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=True)

    async def stop(self) -> None:
        """Close the shared browser. Call once at application shutdown."""
        if self._browser is not None:
            await self._browser.close()
            self._browser = None
        if self._playwright is not None:
            await self._playwright.stop()
            self._playwright = None

    async def render(self, html: str) -> bytes:
        """Render a self-contained HTML document to a full-page PNG.

        Args:
            html: A complete, self-contained HTML document.

        Returns:
            PNG image bytes.

        Raises:
            InfographicRenderError: If the browser is not started or rendering
                fails.
        """
        if self._browser is None:
            raise InfographicRenderError("Renderer is not started")

        # A short initial height lets the full-page screenshot hug the content
        # for short reports; taller infographics expand it automatically.
        context = await self._browser.new_context(
            viewport={"width": _VIEWPORT_WIDTH, "height": 100}
        )
        try:
            page = await context.new_page()
            await page.set_content(html, wait_until="networkidle")
            return await page.screenshot(full_page=True, type="png")
        except PlaywrightError as exc:
            raise InfographicRenderError("Failed to render infographic") from exc
        finally:
            await context.close()
