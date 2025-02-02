import os
import time
import random
import pandas as pd
import requests

# from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver
from selenium.webdriver.support import expected_conditions as EC

rand = [0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5]


class EtsyScraper:
    """
    A class designed to scrape data from Etsy shop AboutPosts.

    Attributes:
        urls (list): List of base URLs to scrape from.
        headers (dict): Custom headers for browser simulation, including user agent and referer.
    """

    def __init__(self, urls, proxy_list=[]):
        self.urls = urls
        self.options = Options()
        self.options.add_argument("--enable-javascript")
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("--incognito")  # Simulate incognito mode
        self.driver = webdriver.Chrome(options=self.options, seleniumwire_options={})

        # Add default headers to all requests
        self.driver.request_interceptor = self._add_custom_headers

        self.proxy_list = proxy_list

        self.data = []
        self.posts = []
        self.postsId = set()
        self.prev_url = "https://www.etsy.com"

    def filter_working_proxies(self):
        """Filters the working proxies from a given list."""
        working_proxies = []
        count = 0
        for proxy in self.proxy_list:
            if self.is_proxy_working(proxy):
                working_proxies.append(proxy)
                count += 1
                print(count)

        return working_proxies

    def is_proxy_working(self, proxy):
        """Checks if a proxy is working."""
        test_url = "https://httpbin.org/ip"

        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}",
        }
        response = requests.get(test_url, proxies=proxies, timeout=2)
        if response.status_code == 200:
            print(f"Proxy {proxy} is working: {response.json()}")
            return True
        return False

    def _add_custom_headers(self, request):
        """Adds custom headers to each request."""

        del request.headers["User-Agent"]
        del request.headers["Accept-Language"]
        del request.headers["Accept-Encoding"]
        del request.headers["Cookie"]

        request.headers["User-Agent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )
        request.headers["Accept"] = (
            "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        )
        request.headers["Accept-Language"] = "en-US,en;q=0.5"
        request.headers["Accept-Encoding"] = "gzip, deflate, br, zstd"

        request.headers["Sec-Fetch-Mode"] = "navigate"
        request.headers["Sec-Fetch-Dest"] = "document"

    def _initialize_driver(self, referer):
        """
        Initializes the Selenium WebDriver with the rotating proxy endpoint.
        """
        self.referer = referer
        self.driver.request_interceptor = self._add_custom_headers

    def scrape(self, output_path="./temp.csv"):
        for url in self.urls:
            try:
                # Reinitialize driver for each request
                self._initialize_driver(url)
                self.driver.get(url + "?ref=anchored_listing#about")

                t = random.uniform(5, 6)  # Random delay
                print(f"Sleeping for {t} seconds")
                time.sleep(t)

                # Fetch the data
                data = (
                    WebDriverWait(self.driver, 5)
                    .until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//span[contains(@data-endpoint, 'AboutPost')]")
                        )
                    )
                    .text
                )

                # Create a single-row DataFrame with the new entry
                new_data = pd.DataFrame({"url": [url], "about": [data]})

                # Append the new entry directly to the CSV
                new_data.to_csv(
                    output_path,
                    mode="a",
                    header=not os.path.exists(output_path),
                    index=False,
                )

            except Exception as e:
                print(f"Error: {e}")

        return

    def logIn(self, passr, usr):
        try:
            time.sleep(2)
            url = "https://www.etsy.com/signin"
            self.driver.get(url)
            time.sleep(2)

            username = self.driver.find_element(By.CSS_SELECTOR, 'input[name="email"]')
            username.send_keys(usr)
            username.send_keys(Keys.ENTER)

            password = self.driver.find_element(
                By.CSS_SELECTOR, 'input[name="password"]'
            )
            password.send_keys(passr)
            password.send_keys(Keys.ENTER)

            time.sleep(5)

            return True
        except Exception as e:
            print(e)

    def write_urls_to_file(self, output_path="./urls.csv"):
        with open(output_path, "w") as f:
            for url in self.urls:
                f.write(url + "#about" + "\n")
