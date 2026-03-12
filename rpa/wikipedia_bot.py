
import argparse
import logging
import sys

import httpx
from playwright.sync_api import sync_playwright

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

DEFAULT_API_URL = "http://localhost:8000"


def search_wikipedia(search_term: str) -> str:
    logger.info("Launching browser")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        # 1. Navigate to Wikipedia
        logger.info("Navigating to Wikipedia")
        page.goto(
            "https://en.wikipedia.org/wiki/Main_Page", wait_until="domcontentloaded"
        )

        # 2. Search for the term
        logger.info("Searching for: %s", search_term)
        search_input = page.locator("#searchInput")
        search_input.fill(search_term)
        search_input.press("Enter")

        # Wait for results page
        page.wait_for_load_state("domcontentloaded")

        # 3. If we landed on a search results page, click the first result
        first_result = page.locator(".mw-search-results .mw-search-result-heading a").first
        if first_result.is_visible():
            logger.info("Search results page detected, clicking first result")
            first_result.click()
            page.wait_for_load_state("domcontentloaded")

        # 4. Extract the first paragraph
        logger.info("Extracting first paragraph …")

        first_paragraph = page.locator(
            "#mw-content-text .mw-parser-output > p:not(.mw-empty-elt)"
        ).first
        first_paragraph.wait_for(timeout=10_000)
        text = first_paragraph.inner_text().strip()

        if not text:
            logger.warning("No text found in first paragraph")
            text = f"Could not extract content for '{search_term}' from Wikipedia."

        logger.info("Extracted %d characters", len(text))
        logger.info("Text preview: %s…", text[:200])

        browser.close()

    return text


def call_summarize_api(text: str, api_url: str) -> dict:
    url = f"{api_url}/assistant/summarize"
    logger.info("Calling API: POST %s", url)

    response = httpx.post(
        url,
        json={"text": text},
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Search Wikipedia and summarize the result via AI",
    )
    parser.add_argument(
        "search_term",
        help="The term to search on Wikipedia",
    )
    parser.add_argument(
        "--api-url",
        default=DEFAULT_API_URL,
        help=f"Backend API base URL (default: {DEFAULT_API_URL})",
    )
    args = parser.parse_args()

    # Step 1: Extract text from Wikipedia
    extracted_text = search_wikipedia(args.search_term)

    if not extracted_text:
        logger.error("No text extracted – aborting")
        sys.exit(1)

    # Step 2: Send to summarization API
    try:
        result = call_summarize_api(extracted_text, args.api_url)
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"\nModel used: {result.get('model_used', 'unknown')}")
        print(f"Request ID: {result.get('request_id', 'N/A')}")
        print(f"\n{result.get('summary', 'No summary returned')}")
        print("\n" + "=" * 60)
    except httpx.HTTPStatusError as exc:
        logger.error("API returned %d: %s", exc.response.status_code, exc.response.text)
        sys.exit(1)
    except httpx.ConnectError:
        logger.error(
            "Could not connect to API at %s – is the backend running", args.api_url
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
