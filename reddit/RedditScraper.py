import random
import time

from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver

from selenium.webdriver.common.by import By
from Post import Post

from selenium.webdriver.common.action_chains import ActionChains

import csv


class ScrapeReddit:
    def __init__(self):
        """
        Initializes the ScrapeReddit class with a Firefox web driver, an empty posts list,
        and a set to track unique post IDs. An ActionChains object is also initialized for scrolling.

        Parameters:
            None
        Returns:
            None
        """
        self.driver = webdriver.Firefox()
        self.posts = []

        self.postids = []
        self.postsId = set()
        self.actions = ActionChains(self.driver)

        self.data = []

    def destroy(self):
        """
        Closes the web driver and exits the ScrapeReddit instance.

        Returns:
            None
        """
        self.driver.close()

    def lazy_scroll(self):
        """
        Scrolls down the webpage repeatedly until the end of the page is reached, then returns the HTML content.

        Returns:
            str: The entire content of the webpage after scrolling to the bottom.
        """
        current_height = self.driver.execute_script(
            "window.scrollTo(0,document.body.scrollHeight);"
        )
        while True:
            self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if (
                new_height == current_height
            ):  # this means we have reached the end of the page!
                html = self.driver.page_source
                break
            current_height = new_height
        return html

    def get_posts(self, subreddits=[], postCount=50):
        """
        Fetches a specified number of posts from each given subreddit and adds them to the internal list.

        Parameters:
            subreddits (list): List of subreddit names to scrape posts from.
            postCount (int): Number of posts to fetch per subreddit. Defaults to 30.

        Returns:
            None
        Raises:
            Exception: If there's an error accessing Reddit's API or the response is malformed.
        """
        for link in subreddits:
            self.driver.get(link)
            self.driver.maximize_window()
            time.sleep(2)

            added_posts = 0

            while added_posts < postCount:
                self._getPosts()
                for card in self.posts:
                    postId = str(card)

                    if postId not in self.postsId:
                        self.postsId.add(postId)

                        try:
                            post = Post(
                                card=card,
                                driver=self.driver,
                            )

                            self.data.append(post.post)
                            added_posts += 1

                        except Exception as e:
                            print(e)
                        time.sleep(1)

                if added_posts > 20:
                    self.driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);"
                    )
                    time.sleep(2)

            fields = [
                "user",
                "title",
                "content",
                "voteCount",
                "commentCount",
                "timestamp",
            ]
            with open("raw_reddit_posts.csv", "w", encoding="utf-8") as file:
                write = csv.writer(file)
                write.writerow(fields)
                write.writerows(self.data)

    def _getPosts(self):
        """
        Fetches the HTML content of posts for a given subreddit.

        Parameters:
            subreddit (str): Name of the subreddit to fetch posts from.
            postCount (int): Number of posts to fetch. Defaults to 30.
            lastPost (str): Link of the last fetched post. Defaults to None.

        Returns:
            list: List of post links found in the HTML content.
        """
        self.posts = self.driver.find_elements(
            By.CSS_SELECTOR, 'article[class="w-full m-0"]'
        )

    def get_data(self, postid):
        """
        Fetches detailed data for a specific Reddit post using its ID.

        Parameters:
            subreddit_id (str): The unique identifier of the Reddit post.

        Returns:
            str: A string containing the full text content and links from Reddit's API response.
        """
        base_url = "https://reddit.com/"
        url = base_url + postid + ".json"
        self.driver.get(url)
        self.driver.maximize_window()
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        text = soup.find("body").get_text()
        time.sleep(3)
        return text

    def get_post_details(self):
        """
        Reads a list of subreddit IDs from a file and initiates the post fetching process for each.

        Parameters:
            file_path (str): Path to the text file containing subreddit IDs.

        Returns:
            None
        """
        jsons = []
        count = 1
        if not self.postids:
            print("No post ids found. Please run get_posts() first.")
            return
        for postid in self.postids:
            print(postid, count)
            text = self.get_data(postid)
            jsons.append(text)
            time.sleep(random.randint(1, 10))
            count += 1

        self.jsons = jsons
        return jsons

    def get_post_info(json_data):
        """
        Gets the post body, all comments and their replies,
        the user IDs of the post, comments, and replies,
        and the timestamps of the post, comments, and replies
        from the JSON data.
        """

        post = json_data[0]["data"]["children"][0]["data"]
        post_body = post["title"]
        post_user = post["author"]
        post_time = post["created_utc"]
        comments = json_data[1]["data"]["children"]
        comments_list = []
        for comment, idx in zip(comments, range(len(comments))):
            comment_body = comment["data"]["body"]
            comment_user = comment["data"]["author"]
            comment_time = comment["data"]["created_utc"]
            comments_list.append(
                {"body": comment_body, "user": comment_user, "time": comment_time}
            )
            comment_replies = []

            # append reply to the comment to which it belongs

            if comment["data"]["replies"] != "":
                replies = comment["data"]["replies"]["data"]["children"]
                for reply in replies:
                    reply_body = reply["data"]["body"]
                    reply_user = reply["data"]["author"]
                    reply_time = reply["data"]["created_utc"]
                    comment_replies.append(
                        {"body": reply_body, "user": reply_user, "time": reply_time}
                    )
            comments_list[idx]["replies"] = comment_replies

        return {
            "post_body": post_body,
            "post_user": post_user,
            "post_time": post_time,
            "comments": comments_list,
        }

    def save_to_csv(self):
        data = {
            "User": [tweet[0] for tweet in self.data],
            "Title": [tweet[1] for tweet in self.data],
            "Content": [tweet[2] for tweet in self.data],
            "Vote Count": [tweet[3] for tweet in self.data],
            "Comment Count": [tweet[4] for tweet in self.data],
            "Timestamp": [tweet[5] for tweet in self.data],
        }

        try:
            with open("reddit_posts.csv", "w", encoding="utf-8") as f:
                f.write(data)
        except Exception:
            pass

        df = pd.DataFrame(data)

        pd.set_option("display.max_colwidth", None)
        df.to_csv("./reddit_posts_df.csv", index=False, encoding="utf-8")

        pass
