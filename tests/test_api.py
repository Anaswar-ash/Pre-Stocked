import pytest

from api import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_analyze_endpoint(client):
    response = client.post('/analyze', data={'ticker': 'AAPL', 'analysis_type': 'simple'})
    assert response.status_code == 200
    assert 'task_id' in response.json

def test_analyze_endpoint_invalid_ticker(client):
    response = client.post('/analyze', data={'ticker': 'INVALID', 'analysis_type': 'simple'})
    assert response.status_code == 400
    assert 'error' in response.json

def test_hybrid_analyze_endpoint(client):
    response = client.post('/hybrid_analyze', data={'ticker': 'AAPL'})
    assert response.status_code == 200
    assert 'task_id' in response.json

def test_hybrid_analyze_endpoint_invalid_ticker(client):
    response = client.post('/hybrid_analyze', data={'ticker': 'INVALID'})
    assert response.status_code == 400
    assert 'error' in response.json
