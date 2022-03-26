import re
import tweepy
import random
import boto3
import json
from collections import defaultdict
import time

key = 'bookdata.json'
bucket = 'trainingdatajson'

s3 = boto3.resource('s3')

obj = s3.Object(bucket, key)
books = json.load(obj.get()['Body'])

# Twitter API credentials
consumer_key = "*****"
consumer_secret = "*****"
access_key = "*****"
access_secret = "*****"


def get_all_tweets(screen_name):
    # Twitter only allows access to a users most recent 3240 tweets with this method

    # authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
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
    outtweets = [[tweet.text.encode("utf-8")] for tweet in alltweets]
    return ([tweet.text for tweet in alltweets])


elon = get_all_tweets('elonmusk')
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
    word1 = random.choice(list(chain.keys()))
    sentence = word1.capitalize()

    # Generate next word in sequence
    while word1[len(word1) - 1] not in ['.', '…', '?', '!'] and len(sentence) < 260:
        word2 = random.choice(chain[word1])
        word1 = word2
        sentence += ' ' + word2

    if sentence[len(sentence) - 1] not in ['.', '…', '?', '!']:
        sentence += '.'
    return sentence

ElonBookDict = markov_chain(elonbooks)

random.seed(int(time.time()))
tweet = generate_sequence(ElonBookDict)

auth = tweepy.OAuthHandler("*****", "*****")
auth.set_access_token("*****",
                      "*****")

# Create API object
api = tweepy.API(auth, wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)

def lambda_handler(event, context):

    return {
    api.update_status(tweet)
    }