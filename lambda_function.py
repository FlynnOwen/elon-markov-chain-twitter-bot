from collections import defaultdict
import random
import os
import json
import re

import tweepy
import boto3


def authorize_tweepy():
    """ Load in Twitter credentials and authoize Tweepy object """

    consumer_key = os.getenv('consumer_key')
    consumer_secret = os.getenv('consumer_secret')
    access_key = os.getenv('access_key')
    access_secret = os.getenv('access_secret')

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key,
                          access_secret)

    api = tweepy.API(auth)
    return api


def load_book_data(key, bucket):
    s3 = boto3.resource('s3')

    obj = s3.Object(bucket, key)
    books = json.load(obj.get()['Body'])

    return books


def get_all_tweets(screen_name, api):
    """Twitter only allows access to a users most recent 3240 tweets with this method"""

    all_tweets = []
    oldest = False

    # keep grabbing tweets until there are no tweets left to grab
    while True:
        if oldest:
            # all subsequent requests use the max_id param to prevent duplicates
            new_tweets = api.user_timeline(screen_name=screen_name, count=200, max_id=oldest)
        else:
            new_tweets = api.user_timeline(screen_name=screen_name, count=200)

        # save most recent tweets
        all_tweets.extend(new_tweets)

        # update the id of the oldest tweet
        oldest = all_tweets[-1].id - 1

        if len(new_tweets) > 0:
            break

    # Save just the text returned from tweets
    return [tweet.text for tweet in all_tweets]


def clean_tweets(tweets):
    for i in range(len(tweets)):
        if tweets[i][len(tweets[i]) - 1] not in ['!', '.', '…', '!', '/?']:
            tweets[i] += '.'

    tweets = ' '.join(tweets)
    tweets = tweets.split(' ')

    for i in range(0, len(tweets)):
        if tweets[i][:5] == 'https':
            tweets[i] = ''
        elif tweets[i][:1] == '@':
            tweets[i] = ''

    tweets = ' '.join(tweets)

    tweets = re.sub('  ', '', tweets)
    tweets = re.sub('\n', ' ', tweets)
    tweets = re.sub("\\'", "'", tweets)

    return tweets


def create_markov_chain(text):
    # Tokenize by word, including punctuation
    words = text.split(' ')

    # Initialize default dict to hold all words
    markov_chain = defaultdict(list)

    for current_word, next_word in zip(words[0:-1], words[1:]):
        markov_chain[current_word].append(next_word)

    # Convert default dict back to dictionary
    markov_chain = dict(markov_chain)
    return markov_chain


def generate_sequence(chain):
    # Capitalize first word
    current_word = random.choice(list(chain.keys()))
    sentence = current_word.capitalize()

    # Generate next word in sequence
    while current_word[-1] not in ['.', '…', '?', '!'] and len(sentence) < 260:
        next_word = random.choice(chain[current_word])
        sentence += ' ' + next_word
        current_word = next_word

    # Put stop word at the end
    if sentence[-1] not in ['.', '…', '?', '!']:
        sentence += '.'

    return sentence


def lambda_handler(event, context):
    api = authorize_tweepy()

    books = load_book_data('bookdata.json', 'trainingdatajson')
    elon = get_all_tweets('elonmusk', api)

    elon = clean_tweets(elon)
    elonbooks = elon + books

    elon_book_dict = create_markov_chain(elonbooks)

    tweet = generate_sequence(elon_book_dict)

    return {
    api.update_status(tweet)
    }