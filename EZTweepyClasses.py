# Twitter Searcher based on account names and keywords
# Step 1. Apply for developer account on twitter
# Step 2. Create an App from the developer menu
# Step 3. Copy your 4 keys from the 'Keys and Tokens' section of your app and paste sequentially starting line 13
# Step 4. You can call objects for both types of search classes below, this can be automated for multiple entries
#         using a list of usernames/keywords and a for loop to iterate through search objects.
# Note: Uncomment the builders when running for the first time 

import tweepy as tw
import os
import re
import pickle
from langdetect import detect

#Enter your keys from developer.twitter.com
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)

NUM_TWEETS = 1000

def format_tweet(text):
    text = re.sub(r'http\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'@\w+ ?', '', text)
    text = text.replace('&amp;','&')
    text = text.replace(" 's", "")
    text = text.replace("\s","")
    return text

def convertList(d):
    l = []
    for k in d:
        l.append(d[k][0])
    return l

class KeyWordSearcher:
    def __init__(self, keyword, number_of_results=NUM_TWEETS):
        self.keyword = keyword
        self.number_of_results = number_of_results
        self.results = {}
        self.read_tweets()
    
    def search(self, date_since = "2019-07-01"):
        print("Getting results for: " + self.keyword)
        word = self.keyword + " -filter:retweets"
        try:
            tweets = tw.Cursor(api.search,
                  q=word,
                  lang="en",
                  since=date_since,
                  result_type='mixed',
                  tweet_mode='extended').items(self.number_of_results)
            for tweet in tweets:
                if(tweet.id in self.results):
                    continue
                else:
                    text = format_tweet(tweet.full_text)
                    self.results[tweet.id] = (text, tweet.user.location)
            print("Done with: " + word.split()[0] + "'s responses")
        except tw.RateLimitError as e:
            print("Twitter api rate limit reached. Waiting for one minute before resuming.")
            time.sleep(60)
            pass
    
    def read_tweets(self):
        try:
            with open(self.keyword + "_tweets",'rb') as fp:
                self.results = pickle.load(fp)
            fp.close()
        except:
            pass
        
    def write_tweets(self):
        with open(self.keyword + "_tweets",'wb') as fp:
            pickle.dump(self.results,fp)
        fp.close()
            
    def keyWordSearch(self):
        self.search()
        return self.results
    
    def searchBuilder(self):
        self.search()
        self.write_tweets()
            
    def print_tweets(self):
        for ft in self.results:
            t = self.results[ft][0]
            lang = detect(t)
            if(lang == 'en'):
                print(t)
    
    def __repr__(self):
        return " ".join(self.results[ft][0] for ft in self.results)
        
        
class AccountTweetBuilder:
    def __init__(self, username, number_of_results=NUM_TWEETS):
        self.username = username
        self.number_of_results = number_of_results
        self.tweet_dict = {}
        self.response_tweet_dict = {}
        self.read_tweets()
        self.read_response_tweets()
    
    def get_tweets(self, date_since = "2019-07-01"):
        #self.response_tweet_dict.update(KeyWordSearcher(self.username, 500).keyWordSearch())
        try:
            tweets = tw.Cursor(api.user_timeline,
                              screen_name=self.username,
                              tweet_mode='extended',
                              result_type='mixed').items(self.number_of_results)
            for tweet in tweets:
                if(tweet.id in self.tweet_dict):
                    continue
                else:
                    text = format_tweet(tweet.full_text)
                    self.tweet_dict[tweet.id] = (text, tweet.user.location)
        except tw.RateLimitError as e:
            print("Twitter api rate limit reached. Waiting for one minute before resuming.")
            time.sleep(60)
            pass
        print("Done with: " + self.username)
            
    def write_tweets(self):
        with open(self.username + "_tweets",'wb') as fp:
            pickle.dump(self.tweet_dict,fp)
        fp.close()
    
    def write_response_tweets(self):
        with open(self.username + "_response_tweets",'wb') as fp:
            pickle.dump(self.response_tweet_dict,fp)
        fp.close()
        
    def read_tweets(self):
        try:
            with open(self.username + "_tweets",'rb') as fp:
                self.tweet_dict = pickle.load(fp)
            fp.close()
        except:
            pass
    
    def read_response_tweets(self):
        try:
            with open(self.username + "_response_tweets",'rb') as fp:
                self.response_tweet_dict = pickle.load(fp)
            fp.close()
        except:
            pass
        
    def tweet_builder(self):
        self.get_tweets()
        self.write_tweets()
        self.write_response_tweets()
        
    def keywordSearcher(self, keywords=[], number_of_results=NUM_TWEETS):
        if(len(keywords) > 0):
            return self.search_by_keyword(keywords, number_of_results)
    
    def print_tweets(self):
        for ft in self.tweet_dict:
            t = self.tweet_dict[ft][0]
            lang = detect(t)
            if(lang == 'en'):
                print(t)
    
    def __repr__(self):
        return " ".join(self.tweet_dict[ft][0] for ft in self.tweet_dict)
    
#Using Account Tweet Builder Class        
atb = AccountTweetBuilder("@INCIndia",100)
#atb.tweet_builder()     #Uncomment this to run twitter API Again, otherwise read from saved tweets
#atb.print_tweets()

#Using KeyWordSearcher Class
kws = KeyWordSearcher("Coronavirus", 100)
#kws.searchBuilder()            #Uncomment this to run twitter API Again, otherwise read from saved tweets
kws.print_tweets()