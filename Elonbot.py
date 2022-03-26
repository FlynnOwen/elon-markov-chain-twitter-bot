import os
import re
import pandas as pd
import tweepy
import random
import twitterscraper as ts
import boto3

from collections import defaultdict

key = 'bookdata.json'
bucket = 'trainingdatajson'

s3 = boto3.resource('s3')

obj = s.Object(bucket,key)
books = json.load(obj.get()['Body'])

tweets = ts.query_tweets_from_user('elonmusk',10000)

df = pd.DataFrame(t.__dict__ for t in tweets)
df = df[df['screen_name'] == 'elonmusk']

elon = df['text'].to_list()
elon = ' '.join(elon)
elon = elon.split()
elon = [i for i in elon if i[0] != '#']
elon = [i for i in elon if i[0] != '.' and len(i) > 1]

for i in range(len(elon)):
    for j in range(len(elon[i])):
        if elon[i][j:j+4] == 'pic.':
            elon[i] = elon[i][:j]
            break
        elif elon[i][j:j+4] == 'http':
            elon[i] = elon[i][:j]
            break
elon = ' '.join(elon)

elon = re.sub(' \.\n', '. ', elon)
elon = re.sub('\n', ' ', elon)
elon = re.sub('\'', ' ', elon)
elon = re.sub('\(', ' ', elon)
elon = re.sub('\)', ' ', elon)
elon = re.sub('_', ' ', elon)
elon = re.sub('_', ' ', elon)
elon = re.sub('"', '', elon)
elon = re.sub('-', '', elon)
elon = re.sub('`', '', elon)
elon = re.sub(' , ', ', ', elon)
elon = re.sub(' ; ',  '; ', elon)
elon = re.sub(' : ', ': ', elon)
elon = re.sub(' ! ', '! ', elon)
elon = re.sub(' \? ', '? ', elon)
elon = re.sub('  ', '', elon)

elon = re.split('(?<=[,.!?;:])',elon)
elon = ' '.join(elon)
elon = re.sub('  ', ' ', elon)

elon = elon*50
elonbooks = books + elon


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
tweet = generate_sequence(ElonBookDict)

tweet