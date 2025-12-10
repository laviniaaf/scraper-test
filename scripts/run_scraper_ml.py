import os
import sys

from scraper.ml_scraper import MLScraper

def main():
    scraper = MLScraper()
    scraper.scrape_produto()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())