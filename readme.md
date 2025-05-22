# IMDb Movie Scraper

This Django-based project scrapes movie data from IMDb and provides a REST API to access and filter the data. It extracts the following movie details:

- Title
- Release Year
- IMDb Rating
- Director(s)
- Cast
- Plot Summary
- Genre

The scraper supports pagination (50 results per page), genre/keyword filtering, and parallel processing for efficiency. The API offers filtering, full-text search, and limit/offset pagination.

## Features

- **Scraper**: Fetches multiple pages from IMDb using Selenium and BeautifulSoup, with support for `--genre`, `--keywords`, and `--max-pages`.
- **API**: REST endpoints for listing movies, filtering by criteria (e.g., `release_year`, `genre`), and full-text search on `title`, `plot_summary`, `directors`, and `cast`.
- **Bonus Functionalities**:
  - **Error Handling/Logging**: Uses Python’s `logging` library, with logs in `scraper.log`.
  - **Unit Tests**: 25 tests (17 scraper, 3 serializer, 5 API) ensure robustness and independence using an in-memory database.
  - **Multiprocessing**: Parallel page fetching with `multiprocessing.Pool` for faster scraping.
  - **Genre/Keyword Support**: Filter movies by genre (e.g., `comedy`) and keywords (e.g., `avengers`).
  - **Full-Text Search**: Search movies by keywords in `title`, `plot_summary`, `directors`, or `cast` (e.g., `?search=mini`).

## Prerequisites

- **Python**: 3.9.6
- **Chrome Browser**: Required for Selenium WebDriver.
- **ChromeDriver**: Automatically installed via `webdriver_manager`.
- **Virtual Environment**: Recommended for dependency isolation.
- **Operating System**: Compatible with Windows, macOS, or Linux.

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/tusharsaxena250/imdb_scrapper.git
   cd imdb_scrapper
   ```

2. **Create a Virtual Environment**:
   ```bash
   python3 -m venv scrape_env
   source scrape_env/bin/activate  # On Windows: scrape_env\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   Dependencies include `django`, `djangorestframework`, `django-filter`, `selenium`, `beautifulsoup4`, `webdriver_manager`, and others.

4. **Apply Database Migrations**:
   ```bash
   python manage.py makemigrations movies
   python manage.py migrate
   ```
   The project uses SQLite (`db.sqlite3`) for simplicity.

## Running the Scraper

The scraper is run via a Django management command (`scrapemovies`).

**Command**:
```bash
python manage.py scrapemovies [options]
```

**Options**:
- `--genre`: Filter movies by genre (e.g., `comedy`, `drama`).
- `--keywords`: Filter movies by keyword (e.g., `avengers`, `superhero`).
- `--max-pages`: Maximum number of pages to scrape (default: 2).

**Examples**:
- Scrape comedy movies:
  ```bash
  python manage.py scrapemovies --genre=comedy
  ```
- Scrape movies with keyword “avengers” (2 pages):
  ```bash
  python manage.py scrapemovies --keyword=avengers --max-pages=2
  ```
- Scrape comedy movies with keyword “avengers”:
  ```bash
  python manage.py scrapemovies --genre=comedy --keyword=avengers --max-pages=2
  ```

The scraper stops if no more data is available and logs details to `scraper.log`.

## Running the Server

Start the Django development server to access the API.

**Command**:
```bash
python manage.py runserver
```

The server runs at `http://localhost:8000`.

## API Endpoints

- **List Movies**:
  ```
  GET http://localhost:8000/api/movies/
  ```
  Returns all movies with pagination (10 per page).

- **Pagination**:
  ```
  GET http://localhost:8000/api/movies/?limit=5&offset=10
  ```
  Returns 5 movies, starting from the 11th.

- **Filtering**:
  ```
  GET http://localhost:8000/api/movies/?release_year=2025
  GET http://localhost:8000/api/movies/?genre=comedy&imdb_rating__gte=7.0
  ```
  Supported filters:
  - `genre`: `exact`, `contains`
  - `release_year`: `exact`, `gte`, `lte`
  - `imdb_rating`: `exact`, `gte`, `lte`
  - `title`: `exact`, `contains`
  - `directors`: `exact`, `contains`
  - `cast`: `exact`, `contains`

- **Full-Text Search**:
  ```
  GET http://localhost:8000/api/movies/?search=mini
  ```
  Searches `title`, `plot_summary`, `directors`, and `cast`.

**Example**:
```bash
curl "http://localhost:8000/api/movies/?search=Virgin"
```
**Response**:
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Virgin Territory",
      "release_year": 2007,
      "imdb_rating": 4.7,
      "plot_summary": "Young Florentines...",
      "directors": "David Leland",
      "cast": "Hayden Christensen,Mischa Barton",
      "genre": "comedy"
    }
  ]
}
```

## Running Tests

The project includes 25 unit tests to validate scraper, serializer, and API functionality, using an in-memory database for independence.

**Test Files**:
- `test_serializers.py`: 3 tests for `MovieSerializer` (validation of title, rating).
- `test_scraper.py`: 17 tests for `IMDbScraper` (page fetching, parsing, error handling).
- `test_api_filters.py`: 5 tests for API filtering and search (e.g., `genre`, `release_year`, `search`).

**Commands**:
```bash
python manage.py test movies.tests.test_serializers
python manage.py test movies.tests.test_scraper
python manage.py test movies.tests.test_api_filters
```

**Run All Tests**:
```bash
python manage.py test movies.tests
```

## Project Structure

- `movies/models.py`: Defines the `Movie` model.
- `movies/scraper.py`: Implements `IMDbScraper` for fetching and parsing IMDb data.
- `movies/serializers.py`: `MovieSerializer` for data validation and serialization.
- `movies/views.py`: `MovieListView` and `MovieDetailView` for API endpoints.
- `movies/urls.py`: URL routing for API.
- `movies/tests/`: Unit tests.
- `settings.py`: Django and REST Framework configuration.
- `scraper.log`: Logs for scraper activity.

  Full Structure
  
  imdb_scrapper
   - imdb_scapper
      - __init__.py
      - settings.py
      - urls.py
   - movies
      - managemnet
          - commands
              - scrapemovies.py
      - tests
          - __init__.py
          - test_api_filters.py
          - test_scraper.py
          - test_seqializers.py
      - __init__.py
      - app.py
      - models.py
      - scraper.py
      - serializers.py
      - urls.py
      - views.py
   - manage.py
   - readme.md
   - requirements.tx
   - scraper.log

## Code Quality

- **Standards**: Adheres to PEP 8, with consistent naming and modular design.
- **Error Handling**: Includes retries for network failures, transaction-based database saves, and detailed logging.
- **Validation**: Enforces valid titles (alphanumeric, specific symbols) and IMDb ratings (0–10).

## Troubleshooting

- **Selenium Errors**:
  - Ensure Chrome and ChromeDriver are installed (`webdriver_manager` handles this).
  - Check `scraper.log` for WebDriver issues.
- **Test Failures**:
  - Clear cache: `find . -name "__pycache__" -exec rm -rf {} +`
  - Verify dependencies: `pip install -r requirements.txt`
- **API Issues**:
  - Check server logs for filter/search errors.
  - Ensure migrations are applied: `python manage.py migrate`

## Bonus Functionalities

- **Logging**: Detailed logs in `scraper.log` for scraping, errors, and validation.
- **Unit Tests**: Comprehensive coverage for scraper, serializer, and API, with mocked network calls.
- **Multiprocessing**: Parallel page fetching reduces scraping time (single-threaded for tests).
- **Genre/Keyword Filtering**: Scrape specific genres or keywords via command-line.
- **Full-Text Search**: API search across multiple fields, enhancing usability.

## License

MIT License. See `LICENSE` file
