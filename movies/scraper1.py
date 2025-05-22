# import requests
# from bs4 import BeautifulSoup
# import time
# from django.db import transaction
# from movies.models import Movie, Person, MoviePerson

# class IMDbScraper:
#     def __init__(self, genre="comedy", max_pages=2):
#         self.base_url = "https://www.imdb.com/search/title/"
#         self.genre = genre
#         self.max_pages = max_pages
#         self.headers = {
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
#         }

#     def get_page(self, page_num=1):
#         params = {
#             "title_type": "feature",
#             "genres": self.genre,
#             "start": (page_num - 1) * 50 + 1  # IMDb uses 50 items per page
#         }
#         try:
#             print(f"Fetching page {page_num} with URL: {self.base_url}?{ '&'.join(f'{k}={v}' for k, v in params.items())}")
#             response = requests.get(self.base_url, headers=self.headers, params=params)
#             response.raise_for_status()
#             print(f"Page {page_num} status code: {response.status_code}")
#             print(f"Page {page_num} content length: {len(response.text)}")
#             return response.text
#         except requests.RequestException as e:
#             print(f"Error fetching page {page_num}: {e}")
#             return None

#     def parse_movie_data(self, html):
#         soup = BeautifulSoup(html, 'html.parser')
#         # Flexible selector for movie items
#         movie_items = soup.select('div[class*="lister-item-content"]') or soup.select('div[class*="ipc-metadata-list-summary-item__c"]')
#         print(f"Found {len(movie_items)} movie items on page")
        
#         movies = []
#         for item in movie_items:
#             movie_data = {}
            
#             # Title
#             title_tag = item.select_one('h3 a') or item.select_one('a[class*="ipc-title-link"]')
#             movie_data['title'] = title_tag.text.strip() if title_tag else None
#             print(f"Title: {movie_data['title']}")
            
#             # Release Year
#             year_tag = item.select_one('span[class*="lister-item-year"]') or item.select_one('span[class*="metadata-item"]')
#             if year_tag and year_tag.text.strip('()').isdigit():
#                 movie_data['release_year'] = int(year_tag.text.strip('()'))
#             else:
#                 movie_data['release_year'] = None
#             print(f"Year: {movie_data['release_year']}")
            
#             # IMDb Rating
#             rating_tag = item.select_one('div[class*="ratings-imdb-rating"] strong') or item.select_one('span[class*="ipc-rating-star"]')
#             movie_data['imdb_rating'] = float(rating_tag.text) if rating_tag and rating_tag.text.replace('.', '').isdigit() else None
#             print(f"Rating: {movie_data['imdb_rating']}")
            
#             # Plot Summary
#             plot_tags = item.select('p[class*="text-muted"]')
#             plot_tag = plot_tags[-1] if plot_tags else None
#             movie_data['plot_summary'] = plot_tag.text.strip() if plot_tag else ""
#             print(f"Plot: {movie_data['plot_summary'][:50]}...")
            
#             # Director(s) and Cast
#             people_tag = item.select_one('p:nth-of-type(3)') or item.select_one('div[class*="metadata-list"]')
#             directors = []
#             cast = []
#             if people_tag:
#                 text = people_tag.text.strip()
#                 if 'Director' in text:
#                     director_links = people_tag.find_all('a', href=lambda x: x and 'tt_ov_dr' in x)
#                     directors = [link.text.strip() for link in director_links]
#                 if 'Stars' in text:
#                     cast_links = people_tag.find_all('a', href=lambda x: x and 'tt_ov_st' in x)
#                     cast = [link.text.strip() for link in cast_links]
#             movie_data['directors'] = directors
#             movie_data['cast'] = cast
#             print(f"Directors: {directors}")
#             print(f"Cast: {cast}")
            
#             if movie_data['title']:
#                 movies.append(movie_data)
        
#         return movies

#     @transaction.atomic
#     def save_to_db(self, movies):
#         print(f"Saving {len(movies)} movies to database")
#         for movie_data in movies:
#             if not movie_data['title']:
#                 continue
                
#             movie, created = Movie.objects.get_or_create(
#                 title=movie_data['title'],
#                 defaults={
#                     'release_year': movie_data['release_year'],
#                     'imdb_rating': movie_data['imdb_rating'],
#                     'plot_summary': movie_data['plot_summary']
#                 }
#             )
            
#             for director_name in movie_data['directors']:
#                 person, _ = Person.objects.get_or_create(name=director_name)
#                 MoviePerson.objects.get_or_create(
#                     movie=movie,
#                     person=person,
#                     role='Director'
#                 )
            
#             for actor_name in movie_data['cast']:
#                 person, _ = Person.objects.get_or_create(name=actor_name)
#                 MoviePerson.objects.get_or_create(
#                     movie=movie,
#                     person=person,
#                     role='Actor'
#                 )

#     def scrape(self):
#         for page in range(1, self.max_pages + 1):
#             print(f"Scraping page {page}...")
#             html = self.get_page(page)
#             if not html:
#                 print(f"No HTML content for page {page}")
#                 continue
                
#             movies = self.parse_movie_data(html)
#             print(f"Extracted {len(movies)} movies from page {page}")
#             self.save_to_db(movies)
            
#             # Stop if no movies were found on this page
#             if not movies:
#                 print(f"No movies found on page {page}. Stopping.")
#                 break
                
#             time.sleep(2)  # Rate limiting

# # if __name__ == "__main__":
# #     scraper = IMDbScraper(genre="comedy", max_pages=2)
# #     scraper.scrape()

# import requests
# from bs4 import BeautifulSoup
# import time
# from django.db import transaction
# from movies.models import Movie, Person, MoviePerson

# class IMDbScraper:
#     def __init__(self, genre="comedy", max_pages=2, stdout=None):
#         self.base_url = "https://www.imdb.com/search/title/"
#         self.genre = genre
#         self.max_pages = max_pages
#         self.stdout = stdout or print
#         self.headers = {
#             "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
#         }

#     def get_page(self, page_num=1):
#         params = {
#             "title_type": "feature",
#             "genres": self.genre,
#             "start": (page_num - 1) * 50 + 1
#         }
#         url = f"{self.base_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
#         try:
#             self.stdout(f"Fetching page {page_num} with URL: {url}")
#             response = requests.get(self.base_url, headers=self.headers, params=params)
#             response.raise_for_status()
#             self.stdout(f"Page {page_num} status code: {response.status_code}")
#             self.stdout(f"Page {page_num} content length: {len(response.text)}")
#             with open(f"page_{page_num}.html", "w", encoding="utf-8") as f:
#                 f.write(response.text)
#             return response.text
#         except requests.RequestException as e:
#             self.stdout(f"Error fetching page {page_num}: {e}")
#             return None

#     def parse_movie_data(self, html):
#         soup = BeautifulSoup(html, 'html.parser')
#         movie_items = soup.select('div[class*="ipc-metadata-list-summary-item__c"]') or soup.select('div[class*="lister-item-content"]')
#         self.stdout(f"Found {len(movie_items)} movie items on page")
        
#         movies = []
#         for idx, item in enumerate(movie_items, 1):
#             movie_data = {}
#             title_tag = item.select_one('a[class*="ipc-title-link"]') or item.select_one('h3 a')
#             movie_data['title'] = title_tag.text.strip() if title_tag else None
#             self.stdout(f"Item {idx} - Title: {movie_data['title']}")
            
#             year_tag = item.select_one('span[class*="metadata-item"]') or item.select_one('span[class*="lister-item-year"]')
#             if year_tag:
#                 year_text = year_tag.text.strip('()')
#                 movie_data['release_year'] = int(year_text) if year_text.isdigit() else None
#             else:
#                 movie_data['release_year'] = None
#             self.stdout(f"Item {idx} - Year: {movie_data['release_year']}")
            
#             rating_tag = item.select_one('span[class*="ipc-rating-star"]') or item.select_one('div[class*="ratings-imdb-rating"] strong')
#             rating_text = rating_tag.text.strip() if rating_tag else None
#             movie_data['imdb_rating'] = float(rating_text) if rating_text and rating_text.replace('.', '').replace('-', '').isdigit() else None
#             self.stdout(f"Item {idx} - Rating: {movie_data['imdb_rating']}")
            
#             plot_tags = item.select('div[class*="ipc-html-content-inner-div"]') or item.select('p[class*="text-muted"]')
#             plot_tag = plot_tags[-1] if plot_tags else None
#             movie_data['plot_summary'] = plot_tag.text.strip() if plot_tag else ""
#             self.stdout(f"Item {idx} - Plot: {movie_data['plot_summary'][:50]}...")
            
#             people_tag = item.select_one('div[class*="metadata-list"]') or item.select_one('p:nth-of-type(3)')
#             directors = []
#             cast = []
#             if people_tag:
#                 text = people_tag.text.strip()
#                 if 'Director' in text:
#                     director_links = people_tag.find_all('a', href=lambda x: x and 'tt_ov_dr' in x)
#                     directors = [link.text.strip() for link in director_links]
#                 if 'Stars' in text:
#                     cast_links = people_tag.find_all('a', href=lambda x: x and 'tt_ov_st' in x)
#                     cast = [link.text.strip() for link in cast_links]
#             movie_data['directors'] = directors
#             movie_data['cast'] = cast
#             self.stdout(f"Item {idx} - Directors: {directors}")
#             self.stdout(f"Item {idx} - Cast: {cast}")
            
#             if movie_data['title']:
#                 movies.append(movie_data)
#             else:
#                 self.stdout(f"Item {idx} - Skipped: No title found")
        
#         return movies

#     @transaction.atomic
#     def save_to_db(self, movies):
#         self.stdout(f"Saving {len(movies)} movies to database")
#         saved_count = 0
#         skipped_count = 0
#         for movie_data in movies:
#             if not movie_data['title']:
#                 self.stdout(f"Skipping movie with no title")
#                 continue
#             movie, created = Movie.objects.get_or_create(
#                 title=movie_data['title'],
#                 defaults={
#                     'release_year': movie_data['release_year'],
#                     'imdb_rating': movie_data['imdb_rating'],
#                     'plot_summary': movie_data['plot_summary']
#                 }
#             )
#             if created:
#                 saved_count += 1
#                 self.stdout(f"Saved new movie: {movie_data['title']}")
#             else:
#                 skipped_count += 1
#                 self.stdout(f"Skipped duplicate movie: {movie_data['title']}")
            
#             for director_name in movie_data['directors']:
#                 person, _ = Person.objects.get_or_create(name=director_name)
#                 MoviePerson.objects.get_or_create(
#                     movie=movie,
#                     person=person,
#                     role='Director'
#                 )
#             for actor_name in movie_data['cast']:
#                 person, _ = Person.objects.get_or_create(name=actor_name)
#                 MoviePerson.objects.get_or_create(
#                     movie=movie,
#                     person=person,
#                     role='Actor'
#                 )
#         self.stdout(f"Total saved: {saved_count}, Total skipped (duplicates): {skipped_count}")
#         return saved_count, skipped_count

#     def scrape(self):
#         total_saved = 0
#         for page in range(1, self.max_pages + 1):
#             self.stdout(f"Scraping page {page}...")
#             html = self.get_page(page)
#             if not html:
#                 self.stdout(f"No HTML content for page {page}")
#                 continue
#             movies = self.parse_movie_data(html)
#             self.stdout(f"Extracted {len(movies)} movies from page {page}")
#             saved, skipped = self.save_to_db(movies)
#             total_saved += saved
#             if not movies:
#                 self.stdout(f"No movies found on page {page}. Stopping.")
#                 break
#             time.sleep(2)
#         self.stdout(f"Scraping complete. Total movies saved: {total_saved}")

# from django.db import transaction
# from movies.models import Movie, Person, MoviePerson
# from bs4 import BeautifulSoup
# import time
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# class IMDbScraper:
#     def __init__(self, genre="comedy", max_pages=2, stdout=None):
#         self.base_url = "https://www.imdb.com/search/title/"
#         self.genre = genre
#         self.max_pages = max_pages
#         self.stdout = stdout or print
#         self.headers = {
#             "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#             "Accept-Language": "en-US,en;q=0.9"
#         }
#         chrome_options = Options()
#         chrome_options.add_argument("--headless")
#         chrome_options.add_argument(f"user-agent={self.headers['User-Agent']}")
#         self.driver = webdriver.Chrome(options=chrome_options)

#     def get_page(self, page_num=1):
#         params = {
#             "title_type": "feature",
#             "genres": self.genre
#         }
#         url = f"{self.base_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
#         try:
#             self.stdout(f"Fetching page {page_num} with URL: {url}")
#             self.driver.get(url)
#             time.sleep(2)  # Wait for initial load

#             # Click "50 More" button for subsequent pages
#             for i in range(page_num - 1):
#                 try:
#                     load_more_button = WebDriverWait(self.driver, 10).until(
#                         EC.element_to_be_clickable((By.CLASS_NAME, "ipc-see-more__text"))
#                     )
#                     self.stdout(f"Clicking '50 More' button for page {i + 2}")
#                     self.driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
#                     load_more_button.click()
#                     time.sleep(3)  # Wait for new content to load
#                 except Exception as e:
#                     self.stdout(f"Error clicking '50 More' button: {e}")
#                     break

#             html = self.driver.page_source
#             self.stdout(f"Page {page_num} actual URL: {self.driver.current_url}")
#             self.stdout(f"Page {page_num} content length: {len(html)}")
#             with open(f"page_{page_num}.html", "w", encoding="utf-8") as f:
#                 f.write(html)
#             return html
#         except Exception as e:
#             self.stdout(f"Error fetching page {page_num}: {e}")
#             return None

#     def parse_movie_data(self, html):
#         soup = BeautifulSoup(html, 'html.parser')
#         movie_items = soup.select('div[class*="ipc-metadata-list-summary-item__c"]') or soup.select('div[class*="lister-item-content"]')
#         self.stdout(f"Found {len(movie_items)} movie items on page")
        
#         movies = []
#         for idx, item in enumerate(movie_items, 1):
#             movie_data = {}
#             title_tag = item.select_one('a[class*="ipc-title-link"]') or item.select_one('h3 a')
#             movie_data['title'] = title_tag.text.strip() if title_tag else None
#             self.stdout(f"Item {idx} - Title: {movie_data['title']}")
            
#             year_tag = item.select_one('span[class*="metadata-item"]') or item.select_one('span[class*="lister-item-year"]')
#             if year_tag:
#                 year_text = year_tag.text.strip('()')
#                 movie_data['release_year'] = int(year_text) if year_text.isdigit() else None
#             else:
#                 movie_data['release_year'] = None
#             self.stdout(f"Item {idx} - Year: {movie_data['release_year']}")
            
#             rating_tag = item.select_one('span[class*="ipc-rating-star"]') or item.select_one('div[class*="ratings-imdb-rating"] strong')
#             rating_text = rating_tag.text.strip() if rating_tag else None
#             movie_data['imdb_rating'] = float(rating_text) if rating_text and rating_text.replace('.', '').replace('-', '').isdigit() else None
#             self.stdout(f"Item {idx} - Rating: {movie_data['imdb_rating']}")
            
#             plot_tags = item.select('div[class*="ipc-html-content-inner-div"]') or item.select('p[class*="text-muted"]')
#             plot_tag = plot_tags[-1] if plot_tags else None
#             movie_data['plot_summary'] = plot_tag.text.strip() if plot_tag else ""
#             self.stdout(f"Item {idx} - Plot: {movie_data['plot_summary'][:50]}...")
            
#             people_tag = item.select_one('div[class*="metadata-list"]') or item.select_one('p:nth-of-type(3)')
#             directors = []
#             cast = []
#             if people_tag:
#                 text = people_tag.text.strip()
#                 if 'Director' in text:
#                     director_links = people_tag.find_all('a', href=lambda x: x and 'tt_ov_dr' in x)
#                     directors = [link.text.strip() for link in director_links]
#                 if 'Stars' in text:
#                     cast_links = people_tag.find_all('a', href=lambda x: x and 'tt_ov_st' in x)
#                     cast = [link.text.strip() for link in cast_links]
#             movie_data['directors'] = directors
#             movie_data['cast'] = cast
#             self.stdout(f"Item {idx} - Directors: {directors}")
#             self.stdout(f"Item {idx} - Cast: {cast}")
            
#             if movie_data['title']:
#                 movies.append(movie_data)
#             else:
#                 self.stdout(f"Item {idx} - Skipped: No title found")
        
#         if movies:
#             self.stdout(f"First 5 titles: {[m['title'] for m in movies[:5]]}")
#         return movies

#     @transaction.atomic
#     def save_to_db(self, movies):
#         self.stdout(f"Saving {len(movies)} movies to database")
#         saved_count = 0
#         skipped_count = 0
#         for movie_data in movies:
#             if not movie_data['title']:
#                 self.stdout(f"Skipping movie with no title")
#                 continue
#             movie, created = Movie.objects.get_or_create(
#                 title=movie_data['title'],
#                 release_year=movie_data['release_year'],  # Include release_year in lookup
#                 defaults={
#                     'imdb_rating': movie_data['imdb_rating'],
#                     'plot_summary': movie_data['plot_summary']
#                 }
#             )
#             if created:
#                 saved_count += 1
#                 self.stdout(f"Saved new movie: {movie_data['title']} ({movie_data['release_year']})")
#             else:
#                 skipped_count += 1
#                 self.stdout(f"Skipped duplicate movie: {movie_data['title']} ({movie_data['release_year']})")
            
#             for director_name in movie_data['directors']:
#                 person, _ = Person.objects.get_or_create(name=director_name)
#                 MoviePerson.objects.get_or_create(
#                     movie=movie,
#                     person=person,
#                     role='Director'
#                 )
#             for actor_name in movie_data['cast']:
#                 person, _ = Person.objects.get_or_create(name=actor_name)
#                 MoviePerson.objects.get_or_create(
#                     movie=movie,
#                     person=person,
#                     role='Actor'
#                 )
#         self.stdout(f"Total saved: {saved_count}, Total skipped (duplicates): {skipped_count}")
#         return saved_count, skipped_count

#     def scrape(self):
#         total_saved = 0
#         for page in range(1, self.max_pages + 1):
#             self.stdout(f"Scraping page {page}...")
#             html = self.get_page(page)
#             if not html:
#                 self.stdout(f"No HTML content for page {page}")
#                 continue
#             movies = self.parse_movie_data(html)
#             self.stdout(f"Extracted {len(movies)} movies from page {page}")
#             saved, skipped = self.save_to_db(movies)
#             total_saved += saved
#             if not movies:
#                 self.stdout(f"No movies found on page {page}. Stopping.")
#                 break
#             time.sleep(3)
#         self.stdout(f"Scraping complete. Total movies saved: {total_saved}")
#         self.driver.quit()

# from django.db import transaction
# from movies.models import Movie, Person, MoviePerson
# from bs4 import BeautifulSoup
# import time
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

# class IMDbScraper:
#     def __init__(self, genre="comedy", max_pages=2, stdout=None):
#         self.base_url = "https://www.imdb.com/search/title/"
#         self.genre = genre
#         self.max_pages = max_pages
#         self.stdout = stdout or print
#         self.headers = {
#             "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#             "Accept-Language": "en-US,en;q=0.9"
#         }
#         chrome_options = Options()
#         chrome_options.add_argument("--headless")
#         chrome_options.add_argument(f"user-agent={self.headers['User-Agent']}")
#         self.driver = webdriver.Chrome(options=chrome_options)

#     def get_page(self, page_num=1):
#         params = {
#             "title_type": "feature",
#             "genres": self.genre
#         }
#         url = f"{self.base_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
#         try:
#             self.stdout(f"Fetching page {page_num} with URL: {url}")
#             self.driver.get(url)
#             time.sleep(2)  # Wait for initial load

#             # Click "50 More" button for subsequent pages
#             for i in range(page_num - 1):
#                 try:
#                     load_more_button = WebDriverWait(self.driver, 10).until(
#                         EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.ipc-see-more__button'))
#                     )
#                     self.stdout(f"Clicking '50 More' button for page {i + 2}")
#                     self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", load_more_button)
#                     load_more_button.click()
#                     time.sleep(3)  # Wait for new content to load
#                 except (TimeoutException, ElementClickInterceptedException) as e:
#                     self.stdout(f"Error clicking '50 More' button for page {i + 2}: {e}")
#                     break

#             html = self.driver.page_source
#             self.stdout(f"Page {page_num} actual URL: {self.driver.current_url}")
#             self.stdout(f"Page {page_num} content length: {len(html)}")
#             with open(f"page_{page_num}.html", "w", encoding="utf-8") as f:
#                 f.write(html)
#             return html
#         except Exception as e:
#             self.stdout(f"Error fetching page {page_num}: {e}")
#             return None
#         finally:
#             # Ensure driver is ready for next page
#             self.driver.execute_script("window.scrollTo(0, 0);")

#     def parse_movie_data(self, html):
#         soup = BeautifulSoup(html, 'html.parser')
#         movie_items = soup.select('div[class*="ipc-metadata-list-summary-item__c"]') or soup.select('div[class*="lister-item-content"]')
#         self.stdout(f"Found {len(movie_items)} movie items on page")
        
#         movies = []
#         for idx, item in enumerate(movie_items, 1):
#             movie_data = {}
#             title_tag = item.select_one('a[class*="ipc-title-link"]') or item.select_one('h3 a')
#             movie_data['title'] = title_tag.text.strip() if title_tag else None
#             self.stdout(f"Item {idx} - Title: {movie_data['title']}")
            
#             year_tag = item.select_one('span[class*="metadata-item"]') or item.select_one('span[class*="lister-item-year"]')
#             if year_tag:
#                 year_text = year_tag.text.strip('()')
#                 movie_data['release_year'] = int(year_text) if year_text.isdigit() else None
#             else:
#                 movie_data['release_year'] = None
#             self.stdout(f"Item {idx} - Year: {movie_data['release_year']}")
            
#             rating_tag = item.select_one('span[class*="ipc-rating-star"]') or item.select_one('div[class*="ratings-imdb-rating"] strong')
#             rating_text = rating_tag.text.strip() if rating_tag else None
#             movie_data['imdb_rating'] = float(rating_text) if rating_text and rating_text.replace('.', '').replace('-', '').isdigit() else None
#             self.stdout(f"Item {idx} - Rating: {movie_data['imdb_rating']}")
            
#             plot_tags = item.select('div[class*="ipc-html-content-inner-div"]') or item.select('p[class*="text-muted"]')
#             plot_tag = plot_tags[-1] if plot_tags else None
#             movie_data['plot_summary'] = plot_tag.text.strip() if plot_tag else ""
#             self.stdout(f"Item {idx} - Plot: {movie_data['plot_summary'][:50]}...")
            
#             people_tag = item.select_one('div[class*="metadata-list"]') or item.select_one('p:nth-of-type(3)')
#             directors = []
#             cast = []
#             if people_tag:
#                 text = people_tag.text.strip()
#                 if 'Director' in text:
#                     director_links = people_tag.find_all('a', href=lambda x: x and 'tt_ov_dr' in x)
#                     directors = [link.text.strip() for link in director_links]
#                 if 'Stars' in text:
#                     cast_links = people_tag.find_all('a', href=lambda x: x and 'tt_ov_st' in x)
#                     cast = [link.text.strip() for link in cast_links]
#             movie_data['directors'] = directors
#             movie_data['cast'] = cast
#             self.stdout(f"Item {idx} - Directors: {directors}")
#             self.stdout(f"Item {idx} - Cast: {cast}")
            
#             if movie_data['title']:
#                 movies.append(movie_data)
#             else:
#                 self.stdout(f"Item {idx} - Skipped: No title found")
        
#         if movies:
#             self.stdout(f"First 5 titles: {[m['title'] for m in movies[:5]]}")
#         return movies

#     @transaction.atomic
#     def save_to_db(self, movies):
#         self.stdout(f"Saving {len(movies)} movies to database")
#         saved_count = 0
#         skipped_count = 0
#         for movie_data in movies:
#             if not movie_data['title']:
#                 self.stdout(f"Skipping movie with no title")
#                 continue
#             movie, created = Movie.objects.get_or_create(
#                 title=movie_data['title'],
#                 release_year=movie_data['release_year'],
#                 defaults={
#                     'imdb_rating': movie_data['imdb_rating'],
#                     'plot_summary': movie_data['plot_summary']
#                 }
#             )
#             if created:
#                 saved_count += 1
#                 self.stdout(f"Saved new movie: {movie_data['title']} ({movie_data['release_year']})")
#             else:
#                 skipped_count += 1
#                 self.stdout(f"Skipped duplicate movie: {movie_data['title']} ({movie_data['release_year']})")
            
#             for director_name in movie_data['directors']:
#                 person, _ = Person.objects.get_or_create(name=director_name)
#                 MoviePerson.objects.get_or_create(
#                     movie=movie,
#                     person=person,
#                     role='Director'
#                 )
#             for actor_name in movie_data['cast']:
#                 person, _ = Person.objects.get_or_create(name=actor_name)
#                 MoviePerson.objects.get_or_create(
#                     movie=movie,
#                     person=person,
#                     role='Actor'
#                 )
#         self.stdout(f"Total saved: {saved_count}, Total skipped (duplicates): {skipped_count}")
#         return saved_count, skipped_count

#     def scrape(self):
#         total_saved = 0
#         for page in range(1, self.max_pages + 1):
#             self.stdout(f"Scraping page {page}...")
#             html = self.get_page(page)
#             if not html:
#                 self.stdout(f"No HTML content for page {page}")
#                 continue
#             movies = self.parse_movie_data(html)
#             self.stdout(f"Extracted {len(movies)} movies from page {page}")
#             saved, skipped = self.save_to_db(movies)
#             total_saved += saved
#             if not movies:
#                 self.stdout(f"No movies found on page {page}. Stopping.")
#                 break
#             time.sleep(1)  # Reduced delay since Selenium handles loading
#         self.stdout(f"Scraping complete. Total movies saved: {total_saved}")
#         self.driver.quit()

# from django.db import transaction
# from movies.models import Movie, Person, MoviePerson
# from bs4 import BeautifulSoup
# import time
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
# from webdriver_manager.chrome import ChromeDriverManager

# class IMDbScraper:
#     def __init__(self, genre="comedy", max_pages=2, stdout=None):
#         self.base_url = "https://www.imdb.com/search/title/"
#         self.genre = genre
#         self.max_pages = max_pages
#         self.stdout = stdout or print
#         self.headers = {
#             "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#             "Accept-Language": "en-US,en;q=0.9"
#         }
#         chrome_options = Options()
#         chrome_options.add_argument("--headless")
#         chrome_options.add_argument(f"user-agent={self.headers['User-Agent']}")
#         self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

#     def get_page(self, page_num=1):
#         params = {
#             "title_type": "feature",
#             "genres": self.genre
#         }
#         url = f"{self.base_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
#         try:
#             self.stdout(f"Fetching page {page_num} with URL: {url}")
#             self.driver.get(url)
#             time.sleep(2)  # Wait for initial load

#             # Click "50 More" button for subsequent pages
#             for i in range(page_num - 1):
#                 retries = 3
#                 for attempt in range(retries):
#                     try:
#                         load_more_button = WebDriverWait(self.driver, 10).until(
#                             EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.ipc-see-more__button'))
#                         )
#                         self.stdout(f"Attempt {attempt + 1}: Found '50 More' button for page {i + 2}")
#                         # Scroll to button and verify position
#                         self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", load_more_button)
#                         time.sleep(1)  # Wait for scroll
#                         button_rect = load_more_button.rect
#                         self.stdout(f"Button position: x={button_rect['x']}, y={button_rect['y']}")
#                         # Wait for new movie items to be present
#                         current_movie_count = len(self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="ipc-metadata-list-summary-item__c"]'))
#                         load_more_button.click()
#                         self.stdout(f"Clicked '50 More' button for page {i + 2}")
#                         WebDriverWait(self.driver, 10).until(
#                             lambda driver: len(driver.find_elements(By.CSS_SELECTOR, 'div[class*="ipc-metadata-list-summary-item__c"]')) > current_movie_count
#                         )
#                         self.stdout(f"New movies loaded for page {i + 2}")
#                         break
#                     except (TimeoutException, ElementClickInterceptedException) as e:
#                         self.stdout(f"Attempt {attempt + 1} failed: Error clicking '50 More' button for page {i + 2}: {e}")
#                         if attempt == retries - 1:
#                             self.stdout(f"Failed to click '50 More' after {retries} attempts")
#                             return None
#                         time.sleep(2)  # Wait before retry
#                     except Exception as e:
#                         self.stdout(f"Unexpected error for page {i + 2}: {e}")
#                         return None

#             html = self.driver.page_source
#             self.stdout(f"Page {page_num} actual URL: {self.driver.current_url}")
#             self.stdout(f"Page {page_num} content length: {len(html)}")
#             with open(f"page_{page_num}.html", "w", encoding="utf-8") as f:
#                 f.write(html)
#             return html
#         except Exception as e:
#             self.stdout(f"Error fetching page {page_num}: {e}")
#             return None
#         finally:
#             self.driver.execute_script("window.scrollTo(0, 0);")

#     def parse_movie_data(self, html):
#         soup = BeautifulSoup(html, 'html.parser')
#         movie_items = soup.select('div[class*="ipc-metadata-list-summary-item__c"]') or soup.select('div[class*="lister-item-content"]')
#         self.stdout(f"Found {len(movie_items)} movie items on page")
        
#         movies = []
#         for idx, item in enumerate(movie_items, 1):
#             movie_data = {}
#             title_tag = item.select_one('a[class*="ipc-title-link"]') or item.select_one('h3 a')
#             movie_data['title'] = title_tag.text.strip() if title_tag else None
#             self.stdout(f"Item {idx} - Title: {movie_data['title']}")
            
#             year_tag = item.select_one('span[class*="metadata-item"]') or item.select_one('span[class*="lister-item-year"]')
#             if year_tag:
#                 year_text = year_tag.text.strip('()')
#                 movie_data['release_year'] = int(year_text) if year_text.isdigit() else None
#             else:
#                 movie_data['release_year'] = None
#             self.stdout(f"Item {idx} - Year: {movie_data['release_year']}")
            
#             rating_tag = item.select_one('span[class*="ipc-rating-star"]') or item.select_one('div[class*="ratings-imdb-rating"] strong')
#             rating_text = rating_tag.text.strip() if rating_tag else None
#             movie_data['imdb_rating'] = float(rating_text) if rating_text and rating_text.replace('.', '').replace('-', '').isdigit() else None
#             self.stdout(f"Item {idx} - Rating: {movie_data['imdb_rating']}")
            
#             plot_tags = item.select('div[class*="ipc-html-content-inner-div"]') or item.select('p[class*="text-muted"]')
#             plot_tag = plot_tags[-1] if plot_tags else None
#             movie_data['plot_summary'] = plot_tag.text.strip() if plot_tag else ""
#             self.stdout(f"Item {idx} - Plot: {movie_data['plot_summary'][:50]}...")
            
#             people_tag = item.select_one('div[class*="metadata-list"]') or item.select_one('p:nth-of-type(3)')
#             directors = []
#             cast = []
#             if people_tag:
#                 text = people_tag.text.strip()
#                 if 'Director' in text:
#                     director_links = people_tag.find_all('a', href=lambda x: x and 'tt_ov_dr' in x)
#                     directors = [link.text.strip() for link in director_links]
#                 if 'Stars' in text:
#                     cast_links = people_tag.find_all('a', href=lambda x: x and 'tt_ov_st' in x)
#                     cast = [link.text.strip() for link in cast_links]
#             movie_data['directors'] = directors
#             movie_data['cast'] = cast
#             self.stdout(f"Item {idx} - Directors: {directors}")
#             self.stdout(f"Item {idx} - Cast: {cast}")
            
#             if movie_data['title']:
#                 movies.append(movie_data)
#             else:
#                 self.stdout(f"Item {idx} - Skipped: No title found")
        
#         if movies:
#             self.stdout(f"First 5 titles: {[m['title'] for m in movies[:5]]}")
#         return movies

#     @transaction.atomic
#     def save_to_db(self, movies):
#         self.stdout(f"Saving {len(movies)} movies to database")
#         saved_count = 0
#         skipped_count = 0
#         for movie_data in movies:
#             if not movie_data['title']:
#                 self.stdout(f"Skipping movie with no title")
#                 continue
#             movie, created = Movie.objects.get_or_create(
#                 title=movie_data['title'],
#                 release_year=movie_data['release_year'],
#                 defaults={
#                     'imdb_rating': movie_data['imdb_rating'],
#                     'plot_summary': movie_data['plot_summary']
#                 }
#             )
#             if created:
#                 saved_count += 1
#                 self.stdout(f"Saved new movie: {movie_data['title']} ({movie_data['release_year']})")
#             else:
#                 skipped_count += 1
#                 self.stdout(f"Skipped duplicate movie: {movie_data['title']} ({movie_data['release_year']})")
            
#             for director_name in movie_data['directors']:
#                 person, _ = Person.objects.get_or_create(name=director_name)
#                 MoviePerson.objects.get_or_create(
#                     movie=movie,
#                     person=person,
#                     role='Director'
#                 )
#             for actor_name in movie_data['cast']:
#                 person, _ = Person.objects.get_or_create(name=actor_name)
#                 MoviePerson.objects.get_or_create(
#                     movie=movie,
#                     person=person,
#                     role='Actor'
#                 )
#         self.stdout(f"Total saved: {saved_count}, Total skipped (duplicates): {skipped_count}")
#         return saved_count, skipped_count

#     def scrape(self):
#         total_saved = 0
#         for page in range(1, self.max_pages + 1):
#             self.stdout(f"Scraping page {page}...")
#             html = self.get_page(page)
#             if not html:
#                 self.stdout(f"No HTML content for page {page}")
#                 continue
#             movies = self.parse_movie_data(html)
#             self.stdout(f"Extracted {len(movies)} movies from page {page}")
#             saved, skipped = self.save_to_db(movies)
#             total_saved += saved
#             if not movies:
#                 self.stdout(f"No movies found on page {page}. Stopping.")
#                 break
#             time.sleep(1)
#         self.stdout(f"Scraping complete. Total movies saved: {total_saved}")
#         self.driver.quit()

# from django.db import transaction
# from movies.models import Movie, Person, MoviePerson
# from bs4 import BeautifulSoup
# import time
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
# from webdriver_manager.chrome import ChromeDriverManager

# class IMDbScraper:
#     def __init__(self, genre="comedy", max_pages=2, stdout=None):
#         self.base_url = "https://www.imdb.com/search/title/"
#         self.genre = genre
#         self.max_pages = max_pages
#         self.stdout = stdout or print
#         self.headers = {
#             "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#             "Accept-Language": "en-US,en;q=0.9"
#         }
#         chrome_options = Options()
#         chrome_options.add_argument("--headless")
#         chrome_options.add_argument(f"user-agent={self.headers['User-Agent']}")
#         self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

#     def get_page(self, page_num=1):
#         params = {
#             "title_type": "feature",
#             "genres": self.genre
#         }
#         url = f"{self.base_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
#         try:
#             self.stdout(f"Fetching page {page_num} with URL: {url}")
#             self.driver.get(url)
#             time.sleep(2)  # Wait for initial load

#             # Click "50 More" button for subsequent pages
#             for i in range(page_num - 1):
#                 retries = 3
#                 for attempt in range(retries):
#                     try:
#                         load_more_button = WebDriverWait(self.driver, 10).until(
#                             EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.ipc-see-more__button'))
#                         )
#                         self.stdout(f"Attempt {attempt + 1}: Found '50 More' button for page {i + 2}")
#                         self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", load_more_button)
#                         time.sleep(1)  # Wait for scroll
#                         button_rect = load_more_button.rect
#                         self.stdout(f"Button position: x={button_rect['x']}, y={button_rect['y']}")
#                         current_movie_count = len(self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="ipc-metadata-list-summary-item__c"]'))
#                         load_more_button.click()
#                         self.stdout(f"Clicked '50 More' button for page {i + 2}")
#                         WebDriverWait(self.driver, 10).until(
#                             lambda driver: len(driver.find_elements(By.CSS_SELECTOR, 'div[class*="ipc-metadata-list-summary-item__c"]')) > current_movie_count
#                         )
#                         self.stdout(f"New movies loaded for page {i + 2}")
#                         break
#                     except (TimeoutException, ElementClickInterceptedException) as e:
#                         self.stdout(f"Attempt {attempt + 1} failed: Error clicking '50 More' button for page {i + 2}: {e}")
#                         if attempt == retries - 1:
#                             self.stdout(f"Failed to click '50 More' after {retries} attempts")
#                             return None
#                         time.sleep(2)
#                     except Exception as e:
#                         self.stdout(f"Unexpected error for page {i + 2}: {e}")
#                         return None

#             html = self.driver.page_source
#             self.stdout(f"Page {page_num} actual URL: {self.driver.current_url}")
#             self.stdout(f"Page {page_num} content length: {len(html)}")
#             with open(f"page_{page_num}.html", "w", encoding="utf-8") as f:
#                 f.write(html)
#             return html
#         except Exception as e:
#             self.stdout(f"Error fetching page {page_num}: {e}")
#             return None
#         finally:
#             self.driver.execute_script("window.scrollTo(0, 0);")

#     def parse_movie_data(self, html):
#         soup = BeautifulSoup(html, 'html.parser')
#         movie_items = soup.select('div[class*="ipc-metadata-list-summary-item__c"]') or soup.select('div[class*="lister-item-content"]')
#         self.stdout(f"Found {len(movie_items)} movie items on page")
        
#         movies = []
#         for idx, item in enumerate(movie_items, 1):
#             movie_data = {}
#             title_tag = item.select_one('a[class*="ipc-title-link"]') or item.select_one('h3 a')
#             movie_data['title'] = title_tag.text.strip() if title_tag else None
#             self.stdout(f"Item {idx} - Title: {movie_data['title']}")
            
#             year_tag = item.select_one('span[class*="metadata-item"]') or item.select_one('span[class*="lister-item-year"]')
#             if year_tag:
#                 year_text = year_tag.text.strip('()')
#                 movie_data['release_year'] = int(year_text) if year_text.isdigit() else None
#             else:
#                 movie_data['release_year'] = None
#             self.stdout(f"Item {idx} - Year: {movie_data['release_year']}")
            
#             # Rating extraction
#             rating_tag = (
#                 item.select_one('span[class*="ipc-rating-star"]') or
#                 item.select_one('div[class*="ratings-imdb-rating"] strong') or
#                 item.select_one('span[aria-label*="IMDb rating"]') or
#                 item.select_one('div[data-testid*="rating"]')
#             )
#             rating_text = None
#             if rating_tag:
#                 rating_text = (
#                     rating_tag.get('data-value') or
#                     rating_tag.get('aria-label', '').split()[-1] if rating_tag.get('aria-label') else
#                     rating_tag.text.strip()
#                 )
#             movie_data['imdb_rating'] = float(rating_text) if rating_text and rating_text.replace('.', '').replace('-', '').isdigit() else None
#             self.stdout(f"Item {idx} - Rating: {movie_data['imdb_rating']}")
#             if not movie_data['imdb_rating']:
#                 rating_div = item.select_one('div[class*="sc-"]') or item.select_one('div[class*="ratings-"]')
#                 rating_html = str(rating_div)[:200] if rating_div else 'No rating div'
#                 self.stdout(f"Item {idx} - Rating HTML: {rating_html}")

#             plot_tags = item.select('div[class*="ipc-html-content-inner-div"]') or item.select('p[class*="text-muted"]')
#             plot_tag = plot_tags[-1] if plot_tags else None
#             movie_data['plot_summary'] = plot_tag.text.strip() if plot_tag else ""
#             self.stdout(f"Item {idx} - Plot: {movie_data['plot_summary'][:50]}...")
            
#             # People extraction
#             people_tag = (
#                 item.select_one('div[class*="metadata-list"]') or
#                 item.select_one('p:nth-of-type(3)') or
#                 item.select_one('div[class*="sc-"] div[class*="text-muted"]') or
#                 item.select_one('div[class*="sc-"]')
#             )
#             directors = []
#             cast = []
#             if people_tag:
#                 text = people_tag.text.strip()
#                 self.stdout(f"Item {idx} - People text: {text[:100]}...")
#                 director_links = (
#                     people_tag.find_all('a', href=lambda x: x and 'tt_ov_dr' in x) or
#                     item.select('a[href*="/name/"][href*="tt_ov_dr"]')
#                 )
#                 directors = [link.text.strip() for link in director_links if link.text.strip()]
#                 cast_links = (
#                     people_tag.find_all('a', href=lambda x: x and 'tt_ov_st' in x) or
#                     item.select('a[href*="/name/"][href*="tt_ov_st"]')
#                 )
#                 cast = [link.text.strip() for link in cast_links if link.text.strip()]
#             movie_data['directors'] = directors
#             movie_data['cast'] = cast
#             self.stdout(f"Item {idx} - Directors: {directors}")
#             self.stdout(f"Item {idx} - Cast: {cast}")
#             if not directors and not cast:
#                 item_html = str(item)[:300] if item else 'No item HTML'
#                 self.stdout(f"Item {idx} - Item HTML: {item_html}")

#             # Optional: Scrape movie page for missing data (uncomment to enable)
#             """
#             if not directors and not cast and title_tag and title_tag.get('href'):
#                 movie_url = f"https://www.imdb.com{title_tag['href']}"
#                 self.stdout(f"Item {idx} - Fetching movie page: {movie_url}")
#                 self.driver.get(movie_url)
#                 time.sleep(1)
#                 movie_soup = BeautifulSoup(self.driver.page_source, 'html.parser')
#                 director_links = movie_soup.select('a[href*="/name/"][href*="tt_ov_dr"]')
#                 cast_links = movie_soup.select('a[href*="/name/"][href*="tt_ov_st"]')
#                 directors = [link.text.strip() for link in director_links if link.text.strip()]
#                 cast = [link.text.strip() for link in cast_links if link.text.strip()]
#                 movie_data['directors'] = directors
#                 movie_data['cast'] = cast
#                 self.stdout(f"Item {idx} - Movie page Directors: {directors}")
#                 self.stdout(f"Item {idx} - Movie page Cast: {cast}")
#                 # Reset to search page
#                 self.driver.get(url)
#                 time.sleep(1)
#             """

#             if movie_data['title']:
#                 movies.append(movie_data)
#             else:
#                 self.stdout(f"Item {idx} - Skipped: No title found")
        
#         if movies:
#             self.stdout(f"First 5 titles: {[m['title'] for m in movies[:5]]}")
#         return movies

#     @transaction.atomic
#     def save_to_db(self, movies):
#         self.stdout(f"Saving {len(movies)} movies to database")
#         saved_count = 0
#         skipped_count = 0
#         for movie_data in movies:
#             if not movie_data['title']:
#                 self.stdout(f"Skipping movie with no title")
#                 continue
#             movie, created = Movie.objects.get_or_create(
#                 title=movie_data['title'],
#                 release_year=movie_data['release_year'],
#                 defaults={
#                     'imdb_rating': movie_data['imdb_rating'],
#                     'plot_summary': movie_data['plot_summary']
#                 }
#             )
#             if created:
#                 saved_count += 1
#                 self.stdout(f"Saved new movie: {movie_data['title']} ({movie_data['release_year']})")
#             else:
#                 skipped_count += 1
#                 self.stdout(f"Skipped duplicate movie: {movie_data['title']} ({movie_data['release_year']})")
            
#             for director_name in movie_data['directors']:
#                 person, _ = Person.objects.get_or_create(name=director_name)
#                 MoviePerson.objects.get_or_create(
#                     movie=movie,
#                     person=person,
#                     role='Director'
#                 )
#             for actor_name in movie_data['cast']:
#                 person, _ = Person.objects.get_or_create(name=actor_name)
#                 MoviePerson.objects.get_or_create(
#                     movie=movie,
#                     person=person,
#                     role='Actor'
#                 )
#         self.stdout(f"Total saved: {saved_count}, Total skipped (duplicates): {skipped_count}")
#         return saved_count, skipped_count

#     def scrape(self):
#         total_saved = 0
#         for page in range(1, self.max_pages + 1):
#             self.stdout(f"Scraping page {page}...")
#             html = self.get_page(page)
#             if not html:
#                 self.stdout(f"No HTML content for page {page}")
#                 continue
#             movies = self.parse_movie_data(html)
#             self.stdout(f"Extracted {len(movies)} movies from page {page}")
#             saved, skipped = self.save_to_db(movies)
#             total_saved += saved
#             if not movies:
#                 self.stdout(f"No movies found on page {page}. Stopping.")
#                 break
#             time.sleep(1)
#         self.stdout(f"Scraping complete. Total movies saved: {total_saved}")
#         self.driver.quit()


from django.db import transaction
from movies.models import Movie, Person, MoviePerson
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager

class IMDbScraper:
    def __init__(self, genre="comedy", max_pages=2, stdout=None):
        self.base_url = "https://www.imdb.com/search/title/"
        self.genre = genre
        self.max_pages = max_pages
        self.stdout = stdout or print
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument(f"user-agent={self.headers['User-Agent']}")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.url = ""

    def get_page(self, page_num=1):
        params = {
            "title_type": "feature",
            "genres": self.genre
        }
        self.url = f"{self.base_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
        try:
            self.stdout(f"Fetching page {page_num} with URL: {self.url}")
            self.driver.get(self.url)
            time.sleep(2)  # Wait for initial load

            # Click "50 More" button for subsequent pages
            for i in range(page_num - 1):
                retries = 3
                for attempt in range(retries):
                    try:
                        load_more_button = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.ipc-see-more__button'))
                        )
                        self.stdout(f"Attempt {attempt + 1}: Found '50 More' button for page {i + 2}")
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", load_more_button)
                        time.sleep(1)  # Wait for scroll
                        button_rect = load_more_button.rect
                        self.stdout(f"Button position: x={button_rect['x']}, y={button_rect['y']}")
                        current_movie_count = len(self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="ipc-metadata-list-summary-item__c"]'))
                        load_more_button.click()
                        self.stdout(f"Clicked '50 More' button for page {i + 2}")
                        WebDriverWait(self.driver, 10).until(
                            lambda driver: len(driver.find_elements(By.CSS_SELECTOR, 'div[class*="ipc-metadata-list-summary-item__c"]')) > current_movie_count
                        )
                        self.stdout(f"New movies loaded for page {i + 2}")
                        break
                    except (TimeoutException, ElementClickInterceptedException) as e:
                        self.stdout(f"Attempt {attempt + 1} failed: Error clicking '50 More' button for page {i + 2}: {e}")
                        if attempt == retries - 1:
                            self.stdout(f"Failed to click '50 More' after {retries} attempts")
                            return None
                        time.sleep(2)
                    except Exception as e:
                        self.stdout(f"Unexpected error for page {i + 2}: {e}")
                        return None

            html = self.driver.page_source
            self.stdout(f"Page {page_num} actual URL: {self.driver.current_url}")
            self.stdout(f"Page {page_num} content length: {len(html)}")
            with open(f"page_{page_num}.html", "w", encoding="utf-8") as f:
                f.write(html)
            return html
        except Exception as e:
            self.stdout(f"Error fetching page {page_num}: {e}")
            return None
        finally:
            self.driver.execute_script("window.scrollTo(0, 0);")

    def parse_movie_data(self, html):
        print(html)
        soup = BeautifulSoup(html, 'html.parser')
        movie_items = soup.select('div[class*="ipc-metadata-list-summary-item__c"]') or soup.select('div[class*="lister-item-content"]')
        self.stdout(f"Found {len(movie_items)} movie items on page")
        
        movies = []
        for idx, item in enumerate(movie_items, 1):
            movie_data = {}
            title_tag = item.select_one('a[class*="ipc-title-link"]') or item.select_one('h3 a')
            movie_data['title'] = title_tag.text.strip() if title_tag else None
            self.stdout(f"Item {idx} - Title: {movie_data['title']}")
            
            year_tag = item.select_one('span[class*="metadata-item"]') or item.select_one('span[class*="lister-item-year"]')
            if year_tag:
                year_text = year_tag.text.strip('()')
                movie_data['release_year'] = int(year_text) if year_text.isdigit() else None
            else:
                movie_data['release_year'] = None
            self.stdout(f"Item {idx} - Year: {movie_data['release_year']}")
            
            # Rating extraction
            rating_tag = (
                item.select_one('span[aria-label*="IMDb rating"]') or
                item.select_one('span[class*="ipc-rating-star"]') or
                item.select_one('div[class*="ratings-imdb-rating"] strong') or
                item.select_one('div[data-testid*="rating"]')
            )
            rating_text = None
            if rating_tag:
                rating_text = (
                    rating_tag.get('data-value') or
                    rating_tag.get('aria-label', '').split()[-1] if rating_tag.get('aria-label') else
                    rating_tag.text.strip()
                )
            movie_data['imdb_rating'] = float(rating_text) if rating_text and rating_text.replace('.', '').replace('-', '').isdigit() else None
            self.stdout(f"Item {idx} - Rating: {movie_data['imdb_rating']}")
            if not movie_data['imdb_rating']:
                rating_div = item.select_one('div[class*="sc-"]') or item.select_one('div[class*="ratings-"]')
                rating_html = str(rating_div)[:200] if rating_div else 'No rating div'
                self.stdout(f"Item {idx} - Rating HTML: {rating_html}")

            plot_tags = item.select('div[class*="ipc-html-content-inner-div"]') or item.select('p[class*="text-muted"]')
            plot_tag = plot_tags[-1] if plot_tags else None
            movie_data['plot_summary'] = plot_tag.text.strip() if plot_tag else ""
            self.stdout(f"Item {idx} - Plot: {movie_data['plot_summary'][:50]}...")
            
            # People extraction
            people_tag = (
                item.select_one('div[class*="metadata-list"]') or
                item.select_one('p:nth-of-type(3)') or
                item.select_one('div[class*="sc-"] div[class*="text-muted"]') or
                item.select_one('div[class*="sc-"]') or
                item.select_one('div[data-testid*="credits"]')
            )
            directors = []
            cast = []
            if people_tag:
                text = people_tag.text.strip()
                self.stdout(f"Item {idx} - People text: {text[:100]}...")
                director_links = (
                    people_tag.find_all('a', href=lambda x: x and 'tt_ov_dr' in x) or
                    item.select('a[href*="/name/"][href*="tt_ov_dr"]') or
                    item.select('a[data-testid*="director"]')
                )
                directors = [link.text.strip() for link in director_links if link.text.strip()]
                cast_links = (
                    people_tag.find_all('a', href=lambda x: x and 'tt_ov_st' in x) or
                    item.select('a[href*="/name/"][href*="tt_ov_st"]') or
                    item.select('a[data-testid*="cast"]')
                )
                cast = [link.text.strip() for link in cast_links if link.text.strip()]
            movie_data['directors'] = directors
            movie_data['cast'] = cast
            self.stdout(f"Item {idx} - Directors: {directors}")
            self.stdout(f"Item {idx} - Cast: {cast}")

            # Scrape movie page for missing directors/cast
            if not directors and not cast and title_tag and title_tag.get('href'):
                movie_url = f"https://www.imdb.com{title_tag['href']}"
                self.stdout(f"Item {idx} - Fetching movie page: {movie_url}")
                self.driver.get(movie_url)
                time.sleep(1)
                movie_soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                director_links = (
                    movie_soup.select('a[href*="/name/"][href*="tt_ov_dr"]') or
                    movie_soup.select('a[data-testid*="director"]')
                )
                cast_links = (
                    movie_soup.select('a[href*="/name/"][href*="tt_ov_st"]') or
                    movie_soup.select('a[data-testid*="cast"]')
                )
                directors = [link.text.strip() for link in director_links if link.text.strip()]
                cast = [link.text.strip() for link in cast_links if link.text.strip()]
                movie_data['directors'] = directors
                movie_data['cast'] = cast
                self.stdout(f"Item {idx} - Movie page Directors: {directors}")
                self.stdout(f"Item {idx} - Movie page Cast: {cast}")
                # Reset to search page
                self.driver.get(self.url)
                time.sleep(1)

            if not directors and not cast:
                item_html = str(item)[:500] if item else 'No item HTML'
                self.stdout(f"Item {idx} - Item HTML: {item_html}")

            if movie_data['title']:
                movies.append(movie_data)
            else:
                self.stdout(f"Item {idx} - Skipped: No title found")
        
        if movies:
            self.stdout(f"First 5 titles: {[m['title'] for m in movies[:5]]}")
        return movies

    @transaction.atomic
    def save_to_db(self, movies):
        self.stdout(f"Saving {len(movies)} movies to database")
        saved_count = 0
        skipped_count = 0
        for movie_data in movies:
            if not movie_data['title']:
                self.stdout(f"Skipping movie with no title")
                continue
            movie, created = Movie.objects.get_or_create(
                title=movie_data['title'],
                release_year=movie_data['release_year'],
                defaults={
                    'imdb_rating': movie_data['imdb_rating'],
                    'plot_summary': movie_data['plot_summary']
                }
            )
            if created:
                saved_count += 1
                self.stdout(f"Saved new movie: {movie_data['title']} ({movie_data['release_year']})")
            else:
                skipped_count += 1
                self.stdout(f"Skipped duplicate movie: {movie_data['title']} ({movie_data['release_year']})")
            
            # Save directors
            for director_name in movie_data['directors']:
                if director_name:
                    person, _ = Person.objects.get_or_create(name=director_name)
                    MoviePerson.objects.get_or_create(
                        movie=movie,
                        person=person,
                        role='Director'
                    )
                    self.stdout(f"Linked Director: {director_name} to {movie_data['title']}")
            # Save cast
            for actor_name in movie_data['cast']:
                if actor_name:
                    person, _ = Person.objects.get_or_create(name=actor_name)
                    MoviePerson.objects.get_or_create(
                        movie=movie,
                        person=person,
                        role='Actor'
                    )
                    self.stdout(f"Linked Actor: {actor_name} to {movie_data['title']}")
        self.stdout(f"Total saved: {saved_count}, Total skipped (duplicates): {skipped_count}")
        return saved_count, skipped_count

    def scrape(self):
        total_saved = 0
        for page in range(1, self.max_pages + 1):
            self.stdout(f"Scraping page {page}...")
            html = self.get_page(page)
            if not html:
                self.stdout(f"No HTML content for page {page}")
                continue
            movies = self.parse_movie_data(html)
            self.stdout(f"Extracted {len(movies)} movies from page {page}")
            saved, skipped = self.save_to_db(movies)
            total_saved += saved
            if not movies:
                self.stdout(f"No movies found on page {page}. Stopping.")
                break
            time.sleep(1)
        self.stdout(f"Scraping complete. Total movies saved: {total_saved}")
        self.driver.quit()