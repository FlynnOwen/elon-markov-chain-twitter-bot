import random

from markov_tweet import authorize_tweepy, get_all_tweets, clean_tweets, generate_sequence, create_markov_chain


def test_authorize_tweepy():
    api = authorize_tweepy()
    assert api.auth


def test_get_all_tweets():
    api = authorize_tweepy()
    elon_tweets = get_all_tweets('elonmusk', api)

    # Correct number of tweets
    assert(len(elon_tweets) >= 2500)

    # Not too many duplicates
    assert(len(set(elon_tweets)) >= 2200)

    # Tweets are of type string
    assert type(elon_tweets[0]) == str


def test_clean_tweets():
    expected_result1 = ' My name is Elon! Look at him hes weird. Double Whammy!'
    mock_tweets1 = ['https:www.flynnowen.com',
                    '@Rodney you bastard!',
                    'My name is\n Elon!',
                    'Look at him  hes weird',
                    'Double  \n Whammy!']

    cleaned_mock_tweets1 = clean_tweets(mock_tweets1)
    assert cleaned_mock_tweets1 == expected_result1

    expected_result2 = 'Just a single Tweet.'
    mock_tweets2 = ['Just a single Tweet']

    cleaned_mock_tweets2 = clean_tweets(mock_tweets2)
    assert cleaned_mock_tweets2 == expected_result2


def test_create_markov_chain():
    mock_sentence1 = 'This is a chain. This is a sentence.'
    expected_result1 = {'This': ['is', 'is'], 'is': ['a', 'a'], 'a': ['chain.', 'sentence.'], 'chain.': ['This']}

    mock_markov_chain1 = create_markov_chain(mock_sentence1)

    assert mock_markov_chain1 == expected_result1

    mock_sentence2 = 'This markov chain might have a cycle cycle cycle'
    expected_result2 = {'This': ['markov'], 'markov': ['chain'], 'chain': ['might'], 'might': ['have'], 'have': ['a'], 'a': ['cycle'], 'cycle': ['cycle', 'cycle']}

    mock_markov_chain2 = create_markov_chain(mock_sentence2)
    
    assert mock_markov_chain2 == expected_result2


def test_generate_sequence():
    mock_markov_chain = {'Look': ['at', 'left!', 'sideways'], 'at': ['me!', 'you!', 'my'],
                         'my': ['foot?'], 'sideways': 'before', 'before': ['you!', '12pm.']}

    expected_result1 = 'Look at me!'
    random.seed(2)
    mock_generated_sequence1 = generate_sequence(mock_markov_chain)
    assert expected_result1 == mock_generated_sequence1

    expected_result2 = 'At my foot?'
    random.seed(3)
    mock_generated_sequence2 = generate_sequence(mock_markov_chain)
    assert expected_result2 == mock_generated_sequence2


