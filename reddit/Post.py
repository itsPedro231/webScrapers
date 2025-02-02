from time import sleep
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.common.by import By



class Post:
    def __init__(
        self,
        card: WebDriver,
        driver: WebDriver,
        actions: ActionChains,
        
    ) -> None:
        self.card = card
        self.error = False
        self.post = None
        
        try:
            self.postId = card.find_element(
                "xpath", './/shreddit-post'
                ).get_attribute("id")
        except NoSuchElementException:
            self.error = True
            self.postId = "skip"
        
        try:
            self.user = card.find_element(
                "xpath", './/a[contains(@href, "/user/")]//span[contains(@class, "whitespace-nowrap")]'
                ).text
        except NoSuchElementException:
            self.error = True
            self.user = "skip"
            
        try:
            self.title = card.find_element(
                "xpath", './/a[@slot="title"]'
            ).text
        except NoSuchElementException:
            self.error = True
            self.title = "skip"
            
        try:
            self.content = [
                p.text for p in card.find_elements(
                    "xpath", './/div[@data-post-click-location="text-body"]//p'
                )
            ]
            if len(self.content) == 0:
                try:
                    self.content = card.find_element(
                        "xpath", './/a[@target="_blank"]').text
                except Exception as e: pass
            else:
                self.content = ''.join(self.content)
                
        except NoSuchElementException:
            self.error = True
            self.content = ["skip"] 
            
        def get_shadow_root(element):
            return driver.execute_script('return arguments[0].shadowRoot', element)
        
        shadowRoot = get_shadow_root(driver.find_element(By.ID, self.postId))
        
        try:
            self.voteCount = shadowRoot.find_element(By.CSS_SELECTOR, 'span[data-post-click-location="vote"] faceplate-number').text
        
        except NoSuchElementException:
            self.voteCount = True
            self.voteCount = "skip"
            
        try:
            self.commentCount = shadowRoot.find_element(By.CSS_SELECTOR, 'a[data-post-click-location="comments-button"] faceplate-number').text
        
        except NoSuchElementException:
            self.commentCount = True
            self.commentCount = "skip"
            
        try:
            self.timestamp = card.find_element(
                "xpath", './/time'
            ).get_attribute("datetime")
        except NoSuchElementException:
            self.error = True
            self.timestamp = "skip"
        
        self.post = (
            self.user,
            self.title,
            self.content,
            self.voteCount,
            self.commentCount,
            self.timestamp

        )

        pass