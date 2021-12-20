import os
from src.drive import download_and_move_one_file
from src.properties import USERS
from src.tweet import shitpost, get_last_tweets, retweet_shitpost
from flask import Flask

app = Flask(__name__)


@app.route("/")
def main():
    name = os.environ.get("NAME", "World")
    for user in USERS:
        tweet_list = get_last_tweets(user)
        if len(tweet_list) == 0:
            # no new tweets today
            continue
        file_name = download_and_move_one_file()
        for twitter_id in tweet_list:
            shitpost(file_name, twitter_id)
    retweet_shitpost()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    main()
