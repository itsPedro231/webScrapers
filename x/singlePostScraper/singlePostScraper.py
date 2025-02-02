from typing import Dict
import jmespath
from playwright.sync_api import sync_playwright


def scrape_tweet(url: str) -> dict:
    """
    Scrape a single tweet page for Tweet thread e.g.:
   
    Return parent tweet, reply tweets and recommended tweets
    """
    _xhr_calls = []

    def intercept_response(response):
        """capture all background requests and save them"""
        # we can extract details from background requests
        if response.request.resource_type == "xhr":
            _xhr_calls.append(response)
        return response

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # enable background request intercepting:
        page.on("response", intercept_response)
        # go to url and wait for the page to load
        page.goto(url)
        page.wait_for_selector("[data-testid='tweet']")

        # find all tweet background requests:
        tweet_calls = [f for f in _xhr_calls if "TweetResultByRestId" in f.url]
        for xhr in tweet_calls:
            data = xhr.json()
            return data['data']['tweetResult']['result']
    
    
    

def parse_tweet(data: Dict) -> Dict:
    """Parse Twitter tweet JSON dataset for the most important fields"""
    result = jmespath.search(
        """{
        text: legacy.full_text,
        created_at: legacy.created_at,
        user_id: legacy.user_id_str,
        like_count: legacy.favorite_count,
        retweet_count: legacy.retweet_count,
        view_count: views.count,
        quote_count: legacy.quote_count
        }""",
        data,
    )
    
    return result
        
        
        
if __name__ == "__main__":
    res = scrape_tweet("https://x.com/search?q=Gun Control&src=typed_query")
    
    a = parse_tweet(res)
    
    with open("output.txt", "w", encoding="utf-8") as file:
        file.write(str(a))