import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from movies.scraper import IMDbScraper
from bs4 import BeautifulSoup
from selenium.common.exceptions import WebDriverException, TimeoutException
from movies.models import Movie

class TestIMDbScraper(TestCase):
    def setUp(self):
        self.scraper = IMDbScraper(genre="comedy", keyword="test", max_pages=1)
        self.scraper._test_single_thread = True
        self.sample_html = """
        <div class="ipc-metadata-list-summary-item__c">
            <a class="ipc-title-link" href="/title/tt0435670/">Virgin Territory</a>
            <span class="metadata-item">2007</span>
            <span aria-label="IMDb rating 4.7">4.7</span>
            <div class="ipc-html-content-inner-div">Young Florentines take refuge...</div>
            <div class="metadata-list">
                Director: <a href="/name/nm0001234/?ref_=tt_ov_dr">David Leland</a> |
                Stars: <a href="/name/nm0001235/?ref_=tt_ov_st">Hayden Christensen</a>,
                <a href="/name/nm0001236/?ref_=tt_ov_st">Mischa Barton</a>
            </div>
        </div>
        """
        self.sample_movie_page_html = """
        <div data-testid="title-pc-principal-credit">
            <a href="/name/nm0001234/?ref_=tt_ov_dr">David Leland</a>
            <a href="/name/nm0001235/?ref_=tt_ov_st">Hayden Christensen</a>
            <a href="/name/nm0001236/?ref_=tt_ov_st">Mischa Barton</a>
        </div>
        """

    @patch('movies.scraper.webdriver.Chrome')
    def test_setup_driver(self, mock_chrome):
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        driver = self.scraper.setup_driver()
        mock_chrome.assert_called_once()
        self.assertTrue("--headless" in mock_chrome.call_args[1]['options']._arguments)
        self.assertTrue("user-agent=" in mock_chrome.call_args[1]['options']._arguments[1])

    @patch('movies.scraper.webdriver.Chrome')
    def test_setup_driver_failure(self, mock_chrome):
        mock_chrome.side_effect = WebDriverException("Browser failed")
        with self.assertRaises(WebDriverException):
            self.scraper.setup_driver()

    @patch('movies.scraper.IMDbScraper.setup_driver')
    def test_get_page_success(self, mock_setup_driver):
        mock_driver = MagicMock()
        mock_driver.page_source = self.sample_html
        mock_driver.current_url = "https://www.imdb.com/search/title/?title_type=feature&genres=comedy"
        mock_setup_driver.return_value = mock_driver
        html = self.scraper.get_page(page_num=1)
        self.assertEqual(html, self.sample_html)
        mock_driver.get.assert_called_with("https://www.imdb.com/search/title/?title_type=feature&genres=comedy&keywords=test")
        mock_driver.quit.assert_called_once()

    @patch('movies.scraper.IMDbScraper.setup_driver')
    def test_get_page_no_html(self, mock_setup_driver):
        mock_driver = MagicMock()
        mock_driver.page_source = None
        mock_setup_driver.return_value = mock_driver
        html = self.scraper.get_page(page_num=1)
        self.assertIsNone(html)
        mock_driver.quit.assert_called_once()

    @patch('movies.scraper.IMDbScraper.setup_driver')
    def test_scrape_movie_page_success(self, mock_setup_driver):
        mock_driver = MagicMock()
        mock_driver.page_source = self.sample_movie_page_html
        mock_setup_driver.return_value = mock_driver
        directors, cast = self.scraper.scrape_movie_page("https://www.imdb.com/title/tt0435670/", mock_driver)
        self.assertEqual(directors, ["David Leland"])
        self.assertEqual(cast, ["Hayden Christensen", "Mischa Barton"])
        mock_driver.get.assert_called_with("https://www.imdb.com/title/tt0435670/")

    @patch('movies.scraper.IMDbScraper.setup_driver')
    def test_scrape_movie_page_partial(self, mock_setup_driver):
        mock_driver = MagicMock()
        mock_driver.page_source = """
        <div data-testid="title-pc-principal-credit">
            <a href="/name/nm0001234/?ref_=tt_ov_dr">David Leland</a>
        </div>
        """
        mock_setup_driver.return_value = mock_driver
        directors, cast = self.scraper.scrape_movie_page("https://www.imdb.com/title/tt0435670/", mock_driver)
        self.assertEqual(directors, ["David Leland"])
        self.assertEqual(cast, [])

    @patch('movies.scraper.IMDbScraper.setup_driver')
    def test_scrape_movie_page_timeout(self, mock_setup_driver):
        mock_driver = MagicMock()
        mock_driver.page_source = ""
        mock_driver.get.side_effect = TimeoutException("Timeout")
        mock_setup_driver.return_value = mock_driver
        directors, cast = self.scraper.scrape_movie_page("https://www.imdb.com/title/tt0435670/", mock_driver)
        self.assertEqual(directors, [])
        self.assertEqual(cast, [])

    def test_parse_movie_data_success(self):
        with patch('movies.scraper.IMDbScraper.setup_driver') as mock_setup_driver:
            mock_driver = MagicMock()
            mock_driver.page_source = self.sample_movie_page_html
            mock_setup_driver.return_value = mock_driver
            movies = self.scraper.parse_movie_data(self.sample_html)
            self.assertEqual(len(movies), 1)
            movie = movies[0]
            self.assertEqual(movie['title'], "Virgin Territory")
            self.assertEqual(movie['release_year'], 2007)
            self.assertEqual(movie['imdb_rating'], 4.7)
            self.assertTrue(movie['plot_summary'].startswith("Young Florentines"))
            self.assertEqual(movie['directors'], ["David Leland"])
            self.assertEqual(movie['cast'], ["Hayden Christensen", "Mischa Barton"])

    def test_parse_movie_data_no_movies(self):
        html = "<div>No movies</div>"
        movies = self.scraper.parse_movie_data(html)
        self.assertEqual(movies, [])

    def test_parse_movie_data_invalid_rating(self):
        invalid_html = """
        <div class="ipc-metadata-list-summary-item__c">
            <a class="ipc-title-link" href="/title/tt0435670/">Virgin Territory</a>
            <span class="metadata-item">2007</span>
            <span aria-label="IMDb rating 11.0">11.0</span>
            <div class="ipc-html-content-inner-div">Young Florentines...</div>
        </div>
        """
        with patch('movies.scraper.IMDbScraper.setup_driver') as mock_setup_driver:
            mock_driver = MagicMock()
            mock_driver.page_source = self.sample_movie_page_html
            mock_setup_driver.return_value = mock_driver
            movies = self.scraper.parse_movie_data(invalid_html)
            self.assertEqual(len(movies), 1)
            self.assertIsNone(movies[0]['imdb_rating'])

    def test_parse_movie_data_invalid_title(self):
        invalid_html = """
        <div class="ipc-metadata-list-summary-item__c">
            <a class="ipc-title-link" href="/title/tt0435670/">Invalid@Title#</a>
            <span class="metadata-item">2007</span>
            <span aria-label="IMDb rating 4.7">4.7</span>
            <div class="ipc-html-content-inner-div">Young Florentines...</div>
        </div>
        """
        with patch('movies.scraper.IMDbScraper.setup_driver') as mock_setup_driver:
            mock_driver = MagicMock()
            mock_driver.page_source = self.sample_movie_page_html
            mock_setup_driver.return_value = mock_driver
            movies = self.scraper.parse_movie_data(invalid_html)
            self.assertEqual(len(movies), 0)

    def test_save_to_db_success(self):
        movies = [{
            'title': "Virgin Territory",
            'release_year': 2007,
            'imdb_rating': 4.7,
            'plot_summary': "Young Florentines...",
            'directors': ["David Leland"],
            'cast': ["Hayden Christensen", "Mischa Barton"]
        }]
        saved, skipped = self.scraper.save_to_db(movies)
        self.assertEqual(saved, 1)
        self.assertEqual(skipped, 0)
        movie = Movie.objects.get(title="Virgin Territory")
        self.assertEqual(movie.imdb_rating, 4.7)
        self.assertEqual(movie.directors, "David Leland")
        self.assertEqual(movie.cast, "Hayden Christensen,Mischa Barton")

    def test_save_to_db_duplicate(self):
        Movie.objects.create(
            title="Virgin Territory",
            release_year=2007,
            imdb_rating=4.7,
            plot_summary="",
            directors="",
            cast=""
        )
        movies = [{
            'title': "Virgin Territory",
            'release_year': 2007,
            'imdb_rating': 4.7,
            'plot_summary': "Young Florentines...",
            'directors': ["David Leland"],
            'cast': ["Hayden Christensen", "Mischa Barton"]
        }]
        saved, skipped = self.scraper.save_to_db(movies)
        self.assertEqual(saved, 0)
        self.assertEqual(skipped, 1)
        self.assertEqual(Movie.objects.count(), 1)

    def test_save_to_db_no_title(self):
        movies = [{
            'title': "",
            'release_year': 2007,
            'imdb_rating': 4.7,
            'plot_summary': "Young Florentines...",
            'directors': ["David Leland"],
            'cast': ["Hayden Christensen"]
        }]
        saved, skipped = self.scraper.save_to_db(movies)
        self.assertEqual(saved, 0)
        self.assertEqual(skipped, 0)
        self.assertEqual(Movie.objects.count(), 0)

    @patch('movies.scraper.IMDbScraper.save_to_db')
    @patch('movies.scraper.IMDbScraper.parse_movie_data')
    @patch('movies.scraper.IMDbScraper.get_page')
    @patch('movies.scraper.IMDbScraper.setup_driver')
    def test_scrape_success(self, mock_setup_driver, mock_get_page, mock_parse_movie_data, mock_save_to_db):
        self.scraper._test_single_thread = True
        mock_driver = MagicMock()
        mock_driver.page_source = self.sample_html
        mock_setup_driver.return_value = mock_driver
        mock_get_page.return_value = self.sample_html
        mock_parse_movie_data.return_value = [{
            'title': "Virgin Territory",
            'release_year': 2007,
            'imdb_rating': 4.7,
            'plot_summary': "Young Florentines...",
            'directors': ["David Leland"],
            'cast': ["Hayden Christensen", "Mischa Barton"]
        }]
        mock_save_to_db.return_value = (1, 0)
        total_saved = self.scraper.scrape()
        self.assertEqual(total_saved, 1)
        mock_get_page.assert_called_with(1)
        mock_parse_movie_data.assert_called_with(self.sample_html)
        mock_save_to_db.assert_called_once_with(mock_parse_movie_data.return_value)

    @patch('movies.scraper.IMDbScraper.get_page')
    def test_scrape_no_pages(self, mock_get_page):
        mock_get_page.side_effect = [None]
        total_saved = self.scraper.scrape()
        self.assertEqual(total_saved, 0)

    def test_genre_keyword_customization(self):
        scraper = IMDbScraper(genre="drama", keyword="superhero", max_pages=1)
        with patch('movies.scraper.IMDbScraper.setup_driver') as mock_setup_driver:
            mock_driver = MagicMock()
            mock_driver.page_source = self.sample_html
            mock_setup_driver.return_value = mock_driver
            scraper.get_page(page_num=1)
            mock_driver.get.assert_called_with("https://www.imdb.com/search/title/?title_type=feature&genres=drama&keywords=superhero")

if __name__ == '__main__':
    unittest.main()