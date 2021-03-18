import tweepy
import logging
import json

# TODO: Add support for different languages
# TODO: determine if status is a retweet or not, also add language arg to is_a_valid_q, follow: https://stackoverflow.com/questions/48242267/determine-if-a-tweet-is-a-retweet-or-not

from ApiConfig import CreateApi


from TweetTextAnalyser import TweetTextAnalyser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


class FavRetweetListener(tweepy.StreamListener):
    def __init__(self, api, currency_keywords, inv_link):
        self.api = api
        self.me = api.me()
        # matches = words in a a streamed status
        self.min_en_matches = 3


        if len(currency_keywords) > 0:
            self.currency_keywords = currency_keywords
        else:
            raise Exception("currency_keywords must contain at least 1 value!")

        # used to compare tweet's string similarity
        self.en_queries = ['where do i buy', 'where can you buy', 'where can I get some',
                           'where would you recommend buying']
        # tuple of array containing keys to count
        self.en_keys = ([['where', 'how'], ['can', 'do'], ['you' 'i'], ['buy', 'purchase']], self.min_en_matches)

        self.inv_link = inv_link

    def on_status(self, tweet):
        try:

            tweet_text = tweet.text.lower()
            # print(f'not split: {tweet.text}')
            # print(f'split: {split_tweet_text}')

            if is_a_valid_question(self, tweet_text):
                logger.info(f'Valid question found: {tweet.text}')

                send_reply_message(self, tweet, self.currency_keywords)



        except Exception as e:

            logger.error("Error on fav and retweet", exc_info=True)


# sends a reply to the tweet
def send_reply_message(self, tweet: tweepy.Status, keywords: [str]):
    inv_link = self.inv_link
    temp = json.dumps(tweet.user._json, indent=4)
    temp = json.loads(temp)
    username = '@' + temp['screen_name']
    subject = ''

    # returns mentioned currencies in the tweet
    mentioned_currencies = [x.capitalize() for x in tweet.text if x.lower() in keywords]  # capitalizes words

    # will be assigned to coin(s) mentioned in the tweet
    coin = None

    # if <=2 matches in the tweet
    if len(mentioned_currencies) <= 2:
        coin = ' and '.join(mentioned_currencies) + ' as well as many other cryptocurrencies'

    # capped at mentioning 3 cryptocurrencies in the reply tweet
    else:
        coin = ', '.join(mentioned_currencies[:3]) + ' and many other cryptocurrencies'

    reply_msg = f'{username} You can buy {coin} at Coinbase using their app or website. Use my referral link and we will both get $10 worth of Bitcoin free when you spend $100 on crypto, have a nice day😊 {inv_link}'

    # post tweet
    self.api.update_status(status=reply_msg, in_reply_to_status_id=tweet.id)


# https://symbiosisacademy.org/tutorial-index/python-flatten-nested-lists-tuples-sets/
def flatten_data(object):
    gather = []
    for item in object:
        if isinstance(item, (set, frozenset, list)):
            gather.extend(flatten_data(item))
        else:
            gather.append(item)

    return gather


# counts number of words/keys that are in two data sets
def count_intersection(text_set: set, data):
    intersection = text_set.intersection(set(flatten_data(data)))
    return len(intersection)


# checks if tweet is a valid question based on the queries
def is_a_valid_question(self, tweet_text: str):
    intersection_len = count_intersection(set(tweet_text.split(" ")), self.en_keys[0])
    print(intersection_len)
    if intersection_len >= self.en_keys[1]:

        # checks using sift4
        tta = TweetTextAnalyser()
        return tta.analyse(tweet_text, self.en_queries, self.currency_keywords)
    else:
        return False


def main(keywords, inv_link):
    api = CreateApi()
    tweets_listener = FavRetweetListener(api, keywords, inv_link)
    stream = tweepy.Stream(api.auth, tweets_listener, tweet_mode="extended")
    stream.filter(track=keywords, languages=["en"])


if __name__ == "__main__":

    #ENTER THE CRYPTOCURRENCY COINS YOU WANT THE BOT TO LISTEN TO
    coins = ['bitcoin',
             'ethereum',
             'litecoin',
             'stellar lumens',
             'filecoin',
             'tezos',
             'eos',
             'dai',
             'zcash']

    inv_link = 'YOUR COINBASE REFERRAL INVITE LINK'  # ADD YOUR PERSONAL LINK

    try:
        main(coins, inv_link)

    except Exception as e:
        logger.error('error in main')
