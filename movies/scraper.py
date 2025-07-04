import logging
import time
import random
import django
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from retrying import retry
from multiprocessing import Pool
import multiprocessing
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('imdb_scraper')

class IMDbScraper:
    def __init__(self, genre=None, keyword=None, max_pages=2, stdout=None):
        self.base_url = "https://www.imdb.com/search/title/"
        self.genre = genre
        self.keyword = keyword
        self.max_pages = max_pages
        self.stdout = stdout or logger.info
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }

    def setup_driver(self):
        """Initialize a new Selenium driver."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument(f"user-agent={self.headers['User-Agent']}")
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            return driver
        except WebDriverException as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=10000)
    def get_page(self, page_num=1):
        """Fetch a single page with retry logic."""
        driver = self.setup_driver()
        try:
            params = {
                "title_type": "feature",
            }
            if self.genre:
                params["genres"] = self.genre
            if self.keyword:
                params["keywords"] = self.keyword
            url = f"{self.base_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}" #creating the url along with genre and/or keywords
            self.stdout(f"Fetching page {page_num} with URL: {url}")
            driver.get(url)
            time.sleep(2)

            for i in range(page_num - 1):
                retries = 3
                for attempt in range(retries):
                    try:
                        #searching for the load 50 more button on the IMDB page given tries are 3
                        load_more_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.ipc-see-more__button'))
                        )
                        self.stdout(f"Attempt {attempt + 1}: Found '50 More' button for page {i + 2}")
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", load_more_button)
                        time.sleep(1)
                        button_rect = load_more_button.rect
                        self.stdout(f"Button position: x={button_rect['x']}, y={button_rect['y']}")
                        current_movie_count = len(driver.find_elements(By.CSS_SELECTOR, 'div[class*="ipc-metadata-list-summary-item__c"]'))
                        load_more_button.click()
                        self.stdout(f"Clicked '50 More' button for page {i + 2}")
                        WebDriverWait(driver, 10).until(
                            lambda d: len(d.find_elements(By.CSS_SELECTOR, 'div[class*="ipc-metadata-list-summary-item__c"]')) > current_movie_count
                        )
                        self.stdout(f"New movies loaded for page {i + 2}")
                        break
                    except (TimeoutException, ElementClickInterceptedException) as e:
                        self.stdout(f"Attempt {attempt + 1} failed: Error clicking '50 More' button for page {i + 2}: {e}")
                        if attempt == retries - 1:
                            logger.error(f"Failed to click '50 More' after {retries} attempts for page {i + 2}")
                            return None
                        time.sleep(2)
                    except Exception as e:
                        logger.error(f"Unexpected error for page {i + 2}: {e}")
                        return None

            html = driver.page_source
            self.stdout(f"Page {page_num} actual URL: {driver.current_url}")
            self.stdout(f"Page {page_num} content length: {len(html) if html else 0}")
            if html and isinstance(html, str):
                with open(f"page_{page_num}.html", "w", encoding="utf-8") as f:
                    f.write(html) #writing the html page to local to be used
            else:
                self.stdout(f"Skipping file write for page {page_num}: HTML is None or not a string")
            return html
        except Exception as e:
            logger.error(f"Error fetching page {page_num}: {e}")
            return None
        finally:
            driver.quit()

    @retry(stop_max_attempt_number=2, wait_fixed=2000)
    def scrape_movie_page(self, movie_url, driver):
        """Scrape an individual movie page for directors and cast."""
        try:
            self.stdout(f"Attempting to fetch movie page: {movie_url}")
            driver.get(movie_url)
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid*="title-pc-principal-credit"], table.cast_list, section[data-testid*="title-cast"]'))
            )
            html = driver.page_source
            title_id = movie_url.split('/')[-2]
            with open(f"movie_page_{title_id}.html", "w", encoding="utf-8") as f:
                f.write(html)
            self.stdout(f"Saved movie page HTML: movie_page_{title_id}.html")
            movie_soup = BeautifulSoup(html, 'html.parser')
            director_links = (
                movie_soup.select('a[href*="/name/"][href*="tt_ov_dr"]') or
                movie_soup.select('li[data-testid*="title-pc-principal-credit"] a[href*="/name/"]') or
                movie_soup.select('a[data-testid*="credit-director"]') or
                movie_soup.select('section[data-testid*="title-cast"] a[href*="/name/"]') or
                movie_soup.select('div[data-testid*="title-pc-wide"] a[href*="/name/"]')
            )
            cast_links = (
                movie_soup.select('a[href*="/name/"][href*="tt_ov_st"]') or
                movie_soup.select('table.cast_list a[href*="/name/"]') or
                movie_soup.select('a[data-testid*="credit-actor"]') or
                movie_soup.select('div[data-testid*="title-cast-item"] a[href*="/name/"]') or
                movie_soup.select('section[data-testid*="title-cast"] a[href*="/name/"]')
            )
            directors = [link.text.strip() for link in director_links if link.text.strip()]
            cast = [link.text.strip() for link in cast_links if link.text.strip()]
            self.stdout(f"Movie page Directors: {directors}")
            self.stdout(f"Movie page Cast: {cast}")
            if not directors and not cast:
                credits_html = str(movie_soup.select_one('div[data-testid*="title-pc-principal-credit"], table.cast_list, section[data-testid*="title-cast"]') or '')[:500]
                self.stdout(f"Movie page Credits HTML: {credits_html}")
            return directors, cast
        except Exception as e:
            logger.error(f"Failed to scrape movie page {movie_url}: {e}")
            return [], []

    def parse_movie_item(self, item_html, idx, existing_movies):
        """Parse a single movie item from HTML string."""
        try:
            soup = BeautifulSoup(item_html, 'html.parser')
            movie_data = {}
            title_tag = (
                soup.select_one('a[class*="ipc-title-link"]') or
                soup.select_one('h3 a') or
                soup.select_one('a[href*="/title/tt"]')
            )
            movie_data['title'] = title_tag.text.strip() if title_tag else None
            if not movie_data['title']:
                self.stdout(f"Item {idx} - Skipped: No title found")
                return None
            self.stdout(f"Item {idx} - Title: {movie_data['title']}")
            
            year_tag = soup.select_one('span[class*="metadata-item"]') or soup.select_one('span[class*="lister-item-year"]')
            if year_tag:
                year_text = year_tag.text.strip('()')
                movie_data['release_year'] = int(year_text) if year_text.isdigit() else None
            else:
                movie_data['release_year'] = None
            self.stdout(f"Item {idx} - Year: {movie_data['release_year']}")
            
            # Skip if title and release_year match an existing movie
            if (movie_data['title'], movie_data['release_year']) in existing_movies:
                self.stdout(f"Item {idx} - Skipped: Movie '{movie_data['title']}' ({movie_data['release_year']}) already in database")
                return None

            title_href = title_tag.get('href') if title_tag else None
            self.stdout(f"Item {idx} - Title href: {title_href}")
            
            rating_tag = (
                soup.select_one('span[aria-label*="IMDb rating"]') or
                soup.select_one('span[class*="ipc-rating-star"]') or
                soup.select_one('div[class*="ratings-imdb-rating"] strong') or
                soup.select_one('div[data-testid*="rating"]')
            )
            rating_text = None
            if rating_tag:
                rating_text = (
                    rating_tag.get('data-value') or
                    rating_tag.get('aria-label', '').split()[-1] if rating_tag.get('aria-label') else
                    rating_tag.text.strip()
                )
            try:
                movie_data['imdb_rating'] = float(rating_text) if rating_text and rating_text.replace('.', '', 1).isdigit() else None
                if movie_data['imdb_rating'] is not None and not (0 <= movie_data['imdb_rating'] <= 10):
                    self.stdout(f"Item {idx} - Invalid rating: {movie_data['imdb_rating']}")
                    movie_data['imdb_rating'] = None
                else:
                    self.stdout(f"Item {idx} - Rating: {movie_data['imdb_rating']}")
            except ValueError:
                movie_data['imdb_rating'] = None
            if not movie_data['imdb_rating']:
                rating_div = soup.select_one('div[class*="sc-"]') or soup.select_one('div[class*="ratings-"]')
                rating_html = str(rating_div)[:200] if rating_div else 'No rating div'
                self.stdout(f"Item {idx} - Rating HTML: {rating_html}")

            plot_tags = soup.select('div[class*="ipc-html-content-inner-div"]') or soup.select('p[class*="text-muted"]')
            plot_tag = plot_tags[-1] if plot_tags else None
            movie_data['plot_summary'] = plot_tag.text.strip() if plot_tag else ""
            self.stdout(f"Item {idx} - Plot: {movie_data['plot_summary'][:50]}...")
            
            people_tag = (
                soup.select_one('div[class*="metadata-list"]') or
                soup.select_one('p:nth-of-type(3)') or
                soup.select_one('div[class*="sc-"] div[class*="text-muted"]') or
                soup.select_one('div[class*="sc-"]') or
                soup.select_one('div[data-testid*="credits"]') or
                soup.select_one('div[data-testid*="title-cast"]')
            )
            directors = []
            cast = []
            if people_tag:
                text = people_tag.text.strip()
                self.stdout(f"Item {idx} - People text: {text[:100]}...")
                director_links = (
                    people_tag.find_all('a', href=lambda x: x and 'tt_ov_dr' in x) or
                    soup.select('a[href*="/name/"][href*="tt_ov_dr"]') or
                    soup.select('a[data-testid*="director"]') or
                    soup.select('div[data-testid*="title-cast"] a[href*="/name/"]')
                )
                directors = [link.text.strip() for link in director_links if link.text.strip()]
                cast_links = (
                    people_tag.find_all('a', href=lambda x: x and 'tt_ov_st' in x) or
                    soup.select('a[href*="/name/"][href*="tt_ov_st"]') or
                    soup.select('a[data-testid*="cast"]') or
                    soup.select('div[data-testid*="title-cast"] a[href*="/name/"]')
                )
                cast = [link.text.strip() for link in cast_links if link.text.strip()]
            movie_data['directors'] = directors
            movie_data['cast'] = cast
            self.stdout(f"Item {idx} - Directors: {directors}")
            self.stdout(f"Item {idx} - Cast: {cast}")

            if not directors and not cast and title_tag and title_tag.get('href'):
                self.stdout(f"Item {idx} - Triggering movie page scrape due to empty directors/cast")
                movie_url = f"https://www.imdb.com{title_tag['href']}"
                driver = self.setup_driver()
                try:
                    directors, cast = self.scrape_movie_page(movie_url, driver)
                    movie_data['directors'] = directors
                    movie_data['cast'] = cast
                finally:
                    driver.quit()

            if not directors and not cast:
                item_html = str(soup)[:500] if soup else 'No item HTML'
                self.stdout(f"Item {idx} - Item HTML: {item_html}")

            if movie_data['title']:
                title_pattern = r'^[a-zA-Z0-9\s\-\'\(\):,.!]+$'
                self.stdout(f"Item {idx} - Validating title '{movie_data['title']}' with regex: {title_pattern}")
                if not re.match(title_pattern, movie_data['title']):
                    self.stdout(f"Item {idx} - Invalid title: {movie_data['title']}")
                    return None
                self.stdout(f"Item {idx} - Title validated successfully")
                return movie_data
            else:
                self.stdout(f"Item {idx} - Skipped: No title found")
                return None
        except Exception as e:
            logger.error(f"Error parsing item {idx}: {e}")
            return None

    def parse_movie_data(self, html):
        """Parse all movie items from HTML in parallel, skipping duplicates."""
        if not html:
            self.stdout("No HTML content to parse")
            return []
        try:
            from movies.models import Movie
            # Query existing (title, release_year) pairs from database
            existing_movies = set(Movie.objects.values_list('title', 'release_year'))
            self.stdout(f"Found {len(existing_movies)} existing movies in database")

            soup = BeautifulSoup(html, 'html.parser')
            movie_items = soup.select('div[class*="ipc-metadata-list-summary-item__c"]') or soup.select('div[class*="lister-item-content"]')
            self.stdout(f"Found {len(movie_items)} movie items on page")
            
            movies = []
            processes = max(1, multiprocessing.cpu_count() - 1)
            self.stdout(f"Parsing {len(movie_items)} movie items with {processes} processes")
            with Pool(processes=processes) as pool:
                results = pool.starmap(
                    self.parse_movie_item,
                    [(str(item), idx, existing_movies) for idx, item in enumerate(movie_items, 1)]
                )
            movies = [result for result in results if result is not None]
            
            if movies:
                self.stdout(f"First 5 titles: {[m['title'] for m in movies[:5]]}")
            return movies
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            return []
    

    def save_to_db(self, movies):
        """Saving the scraped data to db in structured format"""
        from django.db import transaction
        from movies.models import Movie

        self.stdout(f"Saving {len(movies)} movies to database")
        saved_count = 0
        skipped_count = 0
        with transaction.atomic():
            for movie_data in movies:
                try:
                    if not movie_data['title']:
                        self.stdout(f"Skipping movie with no title")
                        continue
                    movie, created = Movie.objects.get_or_create(
                        title=movie_data['title'],
                        release_year=movie_data['release_year'],
                        defaults={
                            'imdb_rating': movie_data['imdb_rating'],
                            'plot_summary': movie_data['plot_summary'],
                            'directors': ','.join(movie_data['directors']) if movie_data['directors'] else '',
                            'cast': ','.join(movie_data['cast']) if movie_data['cast'] else '',
                            'genre': self.genre or 'Unknown'
                        }
                    )
                    if created:
                        saved_count += 1
                        self.stdout(f"Saved new movie: {movie_data['title']} ({movie_data['release_year']})")
                    else:
                        skipped_count += 1
                        self.stdout(f"Skipped duplicate movie: {movie_data['title']} ({movie_data['release_year']})")
                except Exception as e:
                    logger.error(f"Error saving movie {movie_data.get('title', 'Unknown')}: {e}")
                    continue
        self.stdout(f"Total saved: {saved_count}, Total skipped (duplicates): {skipped_count}")
        self.stdout(f"Returning from save_to_db: saved={saved_count}, skipped={skipped_count}")
        return saved_count, skipped_count

    def scrape(self):
        """Main scrape function, it scrapes the data store it in db and return the total number of saved movies in the current scrape"""
        total_saved = 0
        try:
            django.setup()
            single_thread = getattr(self, '_test_single_thread', False)
            self.stdout(f"Starting scrape with max_pages={self.max_pages}, single_thread={single_thread}")
            if single_thread:
                self.stdout("Running in single-threaded mode")
                results = [self.get_page(page) for page in range(1, self.max_pages + 1)]
            else:
                self.stdout("Running in multi-threaded mode")
                processes = max(1, multiprocessing.cpu_count() - 1)
                with Pool(processes=processes, initializer=django.setup) as pool:
                    results = pool.map(self.get_page, range(1, self.max_pages + 1))
            
            for page_num, html in enumerate(results, 1):
                self.stdout(f"Processing page {page_num}...")
                if not html:
                    self.stdout(f"No HTML content for page {page_num}")
                    continue
                movies = self.parse_movie_data(html)
                self.stdout(f"Extracted {len(movies)} movies from page {page_num}")
                saved, skipped = self.save_to_db(movies)
                total_saved += saved
                if not movies:
                    self.stdout(f"No movies found on page {page_num}. Stopping.")
                    break
                time.sleep(random.uniform(0.5, 1.5))
            self.stdout(f"Scraping complete. Total movies saved: {total_saved}")
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
        return total_saved