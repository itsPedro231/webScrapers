from selenium.common.exceptions import (
    NoSuchElementException,
)
from selenium.webdriver.chrome.webdriver import WebDriver

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


class Post:
    """A class to represent a Reddit post captured from Selenium.

    This class wraps the output of a Selenium session listening for specific
    post-related elements on a subreddit page. It provides properties and methods
    to access and process the captured data about the post.

    Attributes:
        card: The DOM element representing the Reddit post.
        driver: The Selenium WebDriver instance used to interact with the webpage.
        post: A tuple containing the extracted post information, or "skip" if there was an error.

    Methods:
        __init__: Initializes the Post object and extracts post-related attributes.
    """

    def __init__(
        self,
        card: WebElement,
        driver: WebDriver,
    ) -> None:
        """Initialize a Post instance with the DOM element representing the Reddit post
        and the Selenium WebDriver. Extracts post-related attributes.

        Args:
            card: The DOM element containing the Reddit post to analyze.
            driver: The Selenium WebDriver used to interact with the webpage.

        Returns:
            A tuple containing user info, title, content, vote count, comment count,
            and timestamp if successful; otherwise "skip".
        """
        self.card = card
        self.error = False
        self.post = None

        try:
            self.postId = card.find_element("xpath", ".//shreddit-post").get_attribute(
                "id"
            )
        except NoSuchElementException:
            self.error = True
            self.postId = "skip"

        try:
            self.user = card.find_element(
                "xpath",
                './/a[contains(@href, "/user/")]//span[contains(@class, "whitespace-nowrap")]',
            ).text
        except NoSuchElementException:
            self.error = True
            self.user = "skip"

        try:
            self.title = card.find_element("xpath", './/a[@slot="title"]').text
        except NoSuchElementException:
            self.error = True
            self.title = "skip"

        try:
            self.content = [
                p.text
                for p in card.find_elements(
                    "xpath", './/div[@data-post-click-location="text-body"]//p'
                )
            ]
            if len(self.content) == 0:
                try:
                    self.content = card.find_element(
                        "xpath", './/a[@target="_blank"]'
                    ).text
                except Exception:
                    pass
            else:
                self.content = "".join(self.content)

        except NoSuchElementException:
            self.error = True
            self.content = ["skip"]

        def get_shadow_root(element):
            return driver.execute_script("return arguments[0].shadowRoot", element)

        shadowRoot = get_shadow_root(driver.find_element(By.ID, self.postId))

        try:
            self.voteCount = shadowRoot.find_element(
                By.CSS_SELECTOR,
                'span[data-post-click-location="vote"] faceplate-number',
            ).text

        except NoSuchElementException:
            self.voteCount = True
            self.voteCount = "skip"

        try:
            self.commentCount = shadowRoot.find_element(
                By.CSS_SELECTOR,
                'a[data-post-click-location="comments-button"] faceplate-number',
            ).text

        except NoSuchElementException:
            self.commentCount = True
            self.commentCount = "skip"

        try:
            self.timestamp = card.find_element("xpath", ".//time").get_attribute(
                "datetime"
            )
        except NoSuchElementException:
            self.error = True
            self.timestamp = "skip"

        self.post = (
            self.user,
            self.title,
            self.content,
            self.voteCount,
            self.commentCount,
            self.timestamp,
        )

        pass
