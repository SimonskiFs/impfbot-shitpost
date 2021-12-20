import logging
import os

from twython import Twython
from datetime import date
from properties import (
    SHITPOST_DESTINATION,
    LOG, SCREEN_NAME
)
from auth import (
    CONSUMER_KEY,
    CONSUMER_SECRET,
    ACCESS_TOKEN,
    ACCESS_TOKEN_SECRET
)

twitter = Twython(
    CONSUMER_KEY,
    CONSUMER_SECRET,
    ACCESS_TOKEN,
    ACCESS_TOKEN_SECRET
)

# logging
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(filename=LOG, level=logging.DEBUG, format=FORMAT)


def get_last_tweets(user_name):
    """returns today tweet ids from user_name"""
    res = []
    today = date.today()
    act = today.strftime("%b-%d-%Y").split('-')
    day = act[1]
    month = act[0]
    year = act[2]
    user_timeline = twitter.get_user_timeline(screen_name=user_name, count=10)
    for tweet in user_timeline:
        tweet_date = tweet["created_at"].split()
        tweet_year = tweet_date[5]
        tweet_month = tweet_date[1]
        tweet_day = tweet_date[2]
        if tweet_day == day and tweet_month == month and tweet_year == year:
            res.append((tweet['id'], user_name))
    return res


def shitpost(filename, twitter_id):
    """final shitpost function"""
    image = open(SHITPOST_DESTINATION + filename, 'rb')
    response = twitter.upload_media(media=image)
    media_id = [response['media_id']]
    status = '@' + twitter_id[1]

    # post the reply
    twitter.update_status(status=status,  media_ids=media_id, in_reply_to_status_id=twitter_id[0])
    logging.info("File " + filename + " postet")

    # delete the used picture from local folder
    os.remove(SHITPOST_DESTINATION + filename)


def retweet_shitpost():
    tweets = twitter.get_user_timeline(screen_name=SCREEN_NAME)
    today = date.today()
    act = today.strftime("%b-%d-%Y").split('-')
    day = act[1]
    month = act[0]
    year = act[2]
    for tweet in tweets:
        tweet_date = tweet["created_at"].split()
        tweet_year = tweet_date[5]
        tweet_month = tweet_date[1]
        tweet_day = tweet_date[2]
        if tweet_day == day and tweet_month == month and tweet_year == year:
            twitter.retweet(id=tweet['id'])
            logging.info("retweeted newest shitpost")
            break
