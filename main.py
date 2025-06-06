"""Convenience wrapper to execute the scraping pipeline."""

import asyncio

from src.main import main as scraping_main


def main() -> None:
    """Run the async scraping pipeline using ``asyncio.run``."""
    asyncio.run(scraping_main())


if __name__ == "__main__":
    main()
