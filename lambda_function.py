from collections import defaultdict
import random
import os
import json
import re

import tweepy
import boto3


key = 'bookdata.json'
bucket = 'trainingdatajson'

s3 = boto3.resource('s3')

obj = s3.Object(bucket, key)
books = json.load(obj.get()['Body'])


def authorize_tweepy():
    """ Load in Twitter credentials and authoize Tweepy object """

    consumer_key = os.getenv('consumer_key')
    consumer_secret = os.getenv('consumer_secret')
    access_key = os.getenv('access_key')
    access_secret = os.getenv('access_secret')

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key,
                          access_secret)

    return auth


def get_all_tweets(screen_name, auth):
    """Twitter only allows access to a users most recent 3240 tweets with this method"""

    # authorize twitter, initialize tweepy
    api = tweepy.API(auth)

    # initialize a list to hold all the tweepy Tweets
    alltweets = []

    # make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name=screen_name, count=200)

    # save most recent tweets
    alltweets.extend(new_tweets)

    # save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    # keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
        # all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name=screen_name, count=200, max_id=oldest)

        # save most recent tweets
        alltweets.extend(new_tweets)

        # update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

    # transform the tweepy tweets into a 2D array that will populate the csv
    return [tweet.text for tweet in alltweets]


auth = authorize_tweepy()
elon = get_all_tweets('elonmusk', auth)
for i in range(len(elon)):
    if elon[i][len(elon[i]) - 1] not in ['!', '.', '…', '!', '/?']:
        elon[i] += '.'

elon = ' '.join(elon)
elon = elon.split(' ')

for i in range(0, len(elon)):
    if elon[i][:5] == 'https':
        elon[i] = ''
    elif elon[i][:1] == '@':
        elon[i] = ''

elon = ' '.join(elon)

elon = re.sub('  ', '', elon)
elon = re.sub('\n', ' ', elon)
elon = re.sub("\\'", "'", elon)

elonbooks = elon + books


def markov_chain(text):
    # Tokenize by word, including punctuation
    words = text.split(' ')

    # Initialize default dict to hold all words
    m_dict = defaultdict(list)

    for current_word, next_word in zip(words[0:-1], words[1:]):
        m_dict[current_word].append(next_word)

    # Convert default dict back to dictionary
    m_dict = dict(m_dict)
    return m_dict


def generate_sequence(chain):
    # Capitalize first word
    current_word = random.choice(list(chain.keys()))
    sentence = current_word.capitalize()

    # Generate next word in sequence
    while current_word[len(current_word) - 1] not in ['.', '…', '?', '!'] and len(sentence) < 260:
        next_word = random.choice(chain[current_word])
        sentence += ' ' + next_word
        current_word = next_word

    # Put stop word at the end
    if sentence[-1] not in ['.', '…', '?', '!']:
        sentence += '.'

    return sentence

elon_book_dict = markov_chain(elonbooks)

tweet = generate_sequence(elon_book_dict)

# Create API object
api = tweepy.API(auth, wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)

def lambda_handler(event, context):

    return {
    api.update_status(tweet)
    }