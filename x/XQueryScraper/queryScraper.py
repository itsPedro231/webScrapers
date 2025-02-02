from datetime import datetime
import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver import ChromeOptions, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    NoSuchElementException,
)

from Scroller import Scroller
from Tweet import Tweet


class XScraper:
    """
    A web scraper for extracting tweets from X (formerly Twitter).
    """

    def __init__(self, username: str, password: str) -> None:
        """
        Initializes the XScraper with login credentials and sets up the Selenium WebDriver.

        :param username: X/Twitter username
        :param password: X/Twitter password
        """
        self.username = username
        self.password = password

        self.options = ChromeOptions()
        self.options.add_argument("--start-maximized")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])

        self.driver = webdriver.Chrome(options=self.options)
        self.scroller = Scroller(self.driver)
        self.actions = ActionChains(self.driver)

        self.data = []
        self.posts = []
        self.postsId = set()

        self.loggedIn = self._logIn()

    def _logIn(self) -> bool:
        """
        Logs into X/Twitter using provided credentials.

        :return: True if login is successful, False otherwise
        """
        try:
            url = "https://twitter.com/i/flow/login"
            self.driver.get(url)

            username_field = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, 'input[autocomplete="username"]')
                )
            )
            username_field.send_keys(self.username)
            username_field.send_keys(Keys.ENTER)

            password_field = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, 'input[name="password"]')
                )
            )
            password_field.send_keys(self.password)
            password_field.send_keys(Keys.ENTER)

            time.sleep(5)
            return True
        except Exception:
            return False

    def scrapeSearch(self, query: str, tweetCount: int) -> None:
        """
        Searches for tweets containing the specified query and scrapes the results.

        :param query: Search query string
        :param tweetCount: Amount of posts to be scraped
        """
        url = f"https://twitter.com/search?q={query}&src=typed_query"
        self.driver.get(url)
        time.sleep(3)

        try:
            accept_cookies_btn = self.driver.find_element(
                By.XPATH, "//span[text()='Refuse non-essential cookies']/../../.."
            )
            accept_cookies_btn.click()
        except NoSuchElementException:
            pass

        added_tweets = 0

        while self.scroller.scrolling and added_tweets < tweetCount:
            try:
                self._getXPosts()

                for card in self.posts[-15:]:
                    try:
                        tweet_id = str(card)
                        if tweet_id not in self.postsId:
                            self.postsId.add(tweet_id)

                            tweet = Tweet(
                                card=card,
                                driver=self.driver,
                                actions=self.actions,
                                scrape_poster_details=False,
                            )

                            if not tweet.is_ad:
                                self.data.append(tweet.tweet)
                                added_tweets += 1
                                print(self.data[added_tweets - 1])

                            self.driver.execute_script("scrollBy(0,600)")
                            time.sleep(1)
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)

    def _getXPosts(self) -> None:
        """
        Retrieves tweet elements from the current page.
        """
        self.posts = self.driver.find_elements(
            By.CSS_SELECTOR, 'article[data-testid="tweet"]'
        )

    def getSample(self) -> None:
        """
        Retrieves a small sample of tweets from the Twitter homepage.
        """
        self.driver.get("https://twitter.com/")
        time.sleep(3)

        self._getXPosts()

        for card in self.posts[-15:]:
            self._process_tweet(card)

    def _process_tweet(self, card) -> None:
        """
        Processes a single tweet card, extracting information if it's not an ad.

        :param card: Web element representing a tweet
        """
        try:
            tweet_id = str(card)
            if tweet_id not in self.postsId:
                self.postsId.add(tweet_id)
                tweet = Tweet(
                    card=card,
                    driver=self.driver,
                    actions=self.actions,
                    scrape_poster_details=False,
                )
                if not tweet.is_ad:
                    self.data.append(tweet.tweet)
                    print(self.data[-1])
        except Exception as e:
            print(e)

    def save_to_csv(self) -> None:
        """
        Saves the scraped tweets to a CSV file.
        """
        now = datetime.now()
        folder_path = "./tweets/"

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        print("Saving data...")
        data = {
            "Name": [tweet[0] for tweet in self.data],
            "Handle": [tweet[1] for tweet in self.data],
            "Timestamp": [tweet[2] for tweet in self.data],
            "Content": [tweet[4] for tweet in self.data],
            "Retweets": [tweet[6] for tweet in self.data],
            "Likes": [tweet[7] for tweet in self.data],
            "Views": [tweet[8] for tweet in self.data],
            "Tweet Link": [tweet[13] for tweet in self.data],
        }

        df = pd.DataFrame(data)
        current_time = now.strftime("%Y-%m-%d_%H-%M-%S")
        file_path = f"{folder_path}{current_time}_tweets_1-{len(self.data)}.csv"
        df.to_csv(file_path, index=False, encoding="utf-8")
