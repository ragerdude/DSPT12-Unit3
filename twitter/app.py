import os

import tweepy
from flask import Flask, request, render_template
from .orm_model import DB, Author, Tweet
from sqlalchemy.exc import IntegrityError
from .twitter import upsert_author
import tweepy
import os
import spacy
import pathlib
from .predict import get_most_likely_author

spacy_path = pathlib.Path(pathlib.Path(__file__).parent, 'my_model').absolute()
spacy_model = spacy.load(spacy_path)

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///twitter_db.sqlite3'
    DB.init_app(app)

    @app.route('/')
    def landing():
        return 'welcome to my application'

    # Retrieve Twitter ID and Author Handle
    @app.route('/add_author')
    def add_author():
        author_handle = request.args['author_handle']
        twitter_auth = tweepy.OAuthHandler(os.environ['TWITTER_API_KEY'], os.environ['TWITTER_API_KEY_SECRET'])
        twitter_api = tweepy.API(twitter_auth)
        upsert_author(author_handle=author_handle, twitter_api=twitter_api, spacy_model=spacy_model)
        try:
            return render_template('landing.html', tweets=[], authors=Author.query.all())
        except IntegrityError as e:
            return '{}<br> that id is taken'.format(str(e))

    # Show Tweets from the specific author
    @app.route('/author_handle/show_tweets')
    def show_tweets():
        body = request.args['text']
        author_id = request.args['author_id']
        new_tweet = Tweet(id=id, author_id=author_id, body=body)
        DB.session.add(new_tweet)
        try:
            DB.session.commit()
            return render_template('landing.html', authors=[], tweets=Tweet.query.all())
        except IntegrityError as e:
            return '{}<br> that id is taken'.format(str(e))

    # Adding new tweets
    @app.route('/add_tweet')
    def add_tweet():
        body = request.args['text']
        author_id = request.args['author_id']
        new_tweet = Tweet(id=id, author_id=author_id, body=body)
        DB.session.add(new_tweet)
        try:
            DB.session.commit()
            return render_template('landing.html', authors=[], tweets=Tweet.query.all())
        except IntegrityError as e:
            return '{}<br> that id is taken'.format(str(e))

    @app.route('/classify_post')
    def classify_post():
        tweet_text = request.args['tweet_text']
        most_likely_author = get_most_likely_author(tweet_body=tweet_text, spacy_model=spacy_model)
        return most_likely_author[0]

    @app.route('/reset')
    def reset_db():
        DB.drop_all()
        DB.create_all()
        return 'Database refreshed'

    return app
