# from django.core.management.base import BaseCommand
# from movies.scraper import IMDbScraper

# class Command(BaseCommand):
#     help = 'Scrape IMDb for movies by genre and save to database'

#     def add_arguments(self, parser):
#         parser.add_argument('--genre', type=str, default='comedy', help='Genre to scrape (e.g., comedy, action)')
#         parser.add_argument('--max-pages', type=int, default=2, help='Maximum number of pages to scrape')

#     def handle(self, *args, **options):
#         genre = options['genre']
#         max_pages = options['max_pages']
#         scraper = IMDbScraper(genre=genre, max_pages=max_pages, stdout=self.stdout.write)
#         scraper.scrape()

import logging
from logging.handlers import RotatingFileHandler
import django
from django.core.management.base import BaseCommand
from movies.scraper import IMDbScraper

# Configure logging
logger = logging.getLogger('imdb_scraper')
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('scraper.log', maxBytes=5*1024*1024, backupCount=2)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

class Command(BaseCommand):
    help = 'Scrape movie data from IMDb'

    def add_arguments(self, parser):
        # parser.add_argument('--genre', type=str, default='comedy', help='Genre to scrape (e.g., comedy, drama)')
        parser.add_argument('--genre', type=str, help='Genre to scrape (e.g., comedy, drama)')
        parser.add_argument('--keyword', type=str, help='Keyword to search (e.g., romantic-comedy)')
        parser.add_argument('--max-pages', type=int, default=2, help='Maximum number of pages to scrape')

    def handle(self, *args, **options):
        django.setup()  # Ensure Django is initialized
        genre = options['genre']
        keyword = options['keyword']
        max_pages = options['max_pages']
        logger.info(f"Starting scrape with genre={genre}, keyword={keyword}, max_pages={max_pages}")
        try:
            scraper = IMDbScraper(genre=genre, keyword=keyword, max_pages=max_pages, stdout=logger.info)
            total_saved = scraper.scrape()
            logger.info(f"Scraping completed successfully. Total movies saved: {total_saved}")
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            raise