
from datetime import datetime
import os
import random
import time

from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver

from selenium.webdriver.common.by import By
from Post import Post

from selenium.webdriver.common.action_chains import ActionChains

import csv


subreddits = ["https://www.reddit.com/r/guncontrol/"]

class ScrapeReddit():
    def __init__(self):
        # start headless if you want later on.
        # options = Options()
        self.driver = webdriver.Firefox()
        self.posts = []
       
        self.postids = []
        self.postsId = set()
        self.actions = ActionChains(self.driver)
        
        self.data = []
    
    def lazy_scroll(self):
        current_height = self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
        while True:
            self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
            time.sleep(2)
            new_height = self.driver.execute_script('return document.body.scrollHeight')   
            if new_height == current_height:      # this means we have reached the end of the page!
                html = self.driver.page_source
                break
            current_height = new_height
        return html

    def get_posts(self):
        for link in subreddits:
            self.driver.get(link)
            self.driver.maximize_window()
            time.sleep(2)
            
            added_posts = 0
            
            
            while added_posts < 50:
                self._getPosts()
                for card in self.posts:
                        
                    postId = str(card)
                    
                    
                    if postId not in self.postsId:
                        self.postsId.add(postId)
                        
                        try:    
                            post = Post(
                            card=card,
                            driver=self.driver,
                            actions=self.actions,
                            
                            )
                            
                            self.data.append(post.post)
                            added_posts += 1
                            
                                
                        except Exception as e: print(e) 
                        time.sleep(1)
                    
                if added_posts > 20:
                 
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                        
            fields = ["user", 'title', 'content', 'voteCount', 'commentCount', 'timestamp']
            with open("raw_reddit_posts.csv", "w", encoding='utf-8') as file:
                write = csv.writer(file)
                write.writerow(fields)
                write.writerows(self.data)
        
    def destroy(self):
        self.driver.close()
        
    def _getPosts(self):
        self.posts = self.driver.find_elements(By.CSS_SELECTOR, 'article[class="w-full m-0"]')
            
    def get_data(self, postid):
        base_url = "https://reddit.com/"
        url = base_url + postid + ".json"
        self.driver.get(url)
        self.driver.maximize_window()
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.find('body').get_text()
        time.sleep(3)
        return text
    
    def get_post_details(self):
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

        post = json_data[0]['data']['children'][0]['data']
        post_body = post['title']
        post_user = post['author']
        post_time = post['created_utc']
        comments = json_data[1]['data']['children']
        comments_list = []
        for (comment, idx) in zip(comments, range(len(comments))):
            comment_body = comment['data']['body']
            comment_user = comment['data']['author']
            comment_time = comment['data']['created_utc']
            comments_list.append({'body': comment_body,
                                'user': comment_user,
                                'time': comment_time})
            comment_replies = []

            # append reply to the comment to which it belongs

            if comment['data']['replies'] != '':
                replies = comment['data']['replies']['data']['children']
                for reply in replies:
                    reply_body = reply['data']['body']
                    reply_user = reply['data']['author']
                    reply_time = reply['data']['created_utc']
                    comment_replies.append({'body': reply_body,
                            'user': reply_user, 'time': reply_time})
            comments_list[idx]['replies'] = comment_replies

        return {
            'post_body': post_body,
            'post_user': post_user,
            'post_time': post_time,
            'comments': comments_list,
            }
        
    def save_to_csv(self):
            
        print("parsing")
        data = {
            "User": [tweet[0] for tweet in self.data],
            "Title": [tweet[1] for tweet in self.data],
            "Content": [tweet[2] for tweet in self.data],
            "Vote Count": [tweet[3] for tweet in self.data],
            "Comment Count": [tweet[4] for tweet in self.data],
            "Timestamp": [tweet[5] for tweet in self.data],
        }
        
        try:
            with open("reddit_posts.csv", "w", encoding='utf-8') as f:
                f.write(data)
        except: pass    

        df = pd.DataFrame(data)

        
        pd.set_option("display.max_colwidth", None)
        df.to_csv("./reddit_posts_df.csv", index=False, encoding="utf-8")
        
        pass

if __name__ == "__main__":
    scraper = ScrapeReddit()
    scraper.get_posts()
    scraper.save_to_csv()
    # print(scraper.get_posts())
    # print(scraper.get_post_details())