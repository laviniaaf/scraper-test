import os
import sys
from scraper.shopee_scraper import ShopeeScraper

def main():
    scraper = ShopeeScraper()
    scraper.scrape_produto()
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())