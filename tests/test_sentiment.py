import pytest
from unittest.mock import patch

from api.analysis.sentiment import (
    classify_sentiment, get_finbert_sentiment, get_sentiment_compound_score)


def test_get_sentiment_compound_score():
    assert get_sentiment_compound_score("This is a great stock!") > 0
    assert get_sentiment_compound_score("This is a terrible stock!") < 0
    assert get_sentiment_compound_score("This is a stock.") == 0
    assert get_sentiment_compound_score("") == 0

def test_classify_sentiment():
    assert classify_sentiment(0.5) == "Positive"
    assert classify_sentiment(-0.5) == "Negative"
    assert classify_sentiment(0) == "Neutral"

@patch('api.analysis.sentiment.finbert')
def test_get_finbert_sentiment(mock_finbert):
    # Mock the FinBERT pipeline
    mock_finbert.return_value = [
        {'label': 'positive', 'score': 0.9},
        {'label': 'negative', 'score': 0.8},
        {'label': 'neutral', 'score': 0.7},
    ]

    posts = [
        {'title': 'Post 1'},
        {'title': 'Post 2'},
        {'title': 'Post 3'},
    ]

    # The expected score is (1 - 1 + 0) / 3 = 0
    assert get_finbert_sentiment(posts) == 0

    # Test with no posts
    assert get_finbert_sentiment([]) == 0
