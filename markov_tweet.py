from collections import defaultdict
import random
import os
import json
import re

import tweepy
import boto3


SENTENCE_CONCLUSIONS = {'!', '.', '…', '!', '/?'}


def main():
    # Pull, clean Elons tweets
    api = authorize_tweepy()
    elons_tweets_raw = get_all_tweets('elonmusk', api)
    elon_tweets_clean = clean_tweets(elons_tweets_raw)

    # Load children books, combine with tweets
    books = load_book_data('bookdata.json', 'trainingdatajson')
    elon_books = elon_tweets_clean + books

    # Create 1st order markov chain from combined data
    elon_book_markov_chain = create_markov_chain(elon_books)

    # Randomly generate a sentence and tweet it
    tweet = generate_sequence(elon_book_markov_chain)
    api.update_status(tweet)


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
    """ Read in children's book data from s3"""
    s3 = boto3.resource('s3')

    obj = s3.Object(bucket, key)
    books = json.load(obj.get()['Body'])

    return books


def get_all_tweets(screen_name, api):
    """ Pull 3240 of Elon Musks latest Tweets"""

    all_tweets = []
    oldest = False

    while True:
        if oldest:
            new_tweets = api.user_timeline(screen_name=screen_name, count=200, max_id=oldest)
        else:
            new_tweets = api.user_timeline(screen_name=screen_name, count=200)

        all_tweets.extend(new_tweets)

        # update the id of the oldest tweet
        oldest = all_tweets[-1].id - 1

        if len(new_tweets) > 0:
            break

    return [tweet.text for tweet in all_tweets]


def clean_tweets(tweets):
    """ Delete tweets with links and tags. Otherwise add conclusion to tweet. """
    for i, tweet in enumerate(tweets):
        if tweet[:5] == 'https':
            tweets[i] = ''
        elif tweet[:1] == '@':
            tweets[i] = ''
        elif tweet[-1] not in SENTENCE_CONCLUSIONS:
            tweets[i] += '.'

    tweets = ' '.join(tweets)

    tweets = re.sub('\n', ' ', tweets)
    tweets = re.sub("\\'", "'", tweets)

    return tweets


def create_markov_chain(text):
    """ Create a markov chain using a default dictionary, and transform to dictionary """
    words = text.split(' ')

    markov_chain = defaultdict(list)

    for current_word, next_word in zip(words[0:-1], words[1:]):
        markov_chain[current_word].append(next_word)

    markov_chain = dict(markov_chain)
    return markov_chain


def generate_sequence(chain):
    """ Stochastically generate a sentence from a Markov Chain """
    # Init first word with capital letter
    current_word = random.choice(list(chain.keys()))
    sentence = current_word.capitalize()

    # Generate next word in sequence
    while current_word[-1] not in SENTENCE_CONCLUSIONS and len(sentence) < 260:
        next_word = random.choice(chain[current_word])
        sentence += ' ' + next_word
        current_word = next_word

    # Put full stop at the end of sentence
    if sentence[-1] not in SENTENCE_CONCLUSIONS:
        sentence += '.'

    return sentence


def lambda_main(event, context):
    main()
