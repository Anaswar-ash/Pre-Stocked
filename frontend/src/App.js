import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
    const [ticker, setTicker] = useState('');
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setAnalysis(null);

        const formData = new FormData();
        formData.append('ticker', ticker);

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            if (data.error) {
                setError(data.error);
                setLoading(false);
                return;
            }

            if (data.task_id) {
                pollTaskStatus(data.task_id);
            } else {
                fetchData(ticker);
            }
        } catch (error) {
            setError('Failed to start analysis. Please try again.');
            setLoading(false);
        }
    };

    const pollTaskStatus = (taskId) => {
        const interval = setInterval(async () => {
            try {
                const response = await fetch(`/status/${taskId}`);
                const data = await response.json();

                if (data.state === 'SUCCESS') {
                    clearInterval(interval);
                    fetchData(ticker);
                } else if (data.state === 'FAILURE') {
                    clearInterval(interval);
                    setError('Analysis failed. Please try again.');
                    setLoading(false);
                }
            } catch (error) {
                clearInterval(interval);
                setError('Failed to get analysis status.');
                setLoading(false);
            }
        }, 5000);
    };

    const fetchData = async (ticker) => {
        try {
            const response = await fetch(`/data/${ticker}`);
            const data = await response.json();
            setAnalysis(data);
        } catch (error) {
            setError('Failed to fetch analysis data.');
        }
        setLoading(false);
    };

    return (
        <div className="App">
            <header className="App-header">
                <h1>Stock Analysis</h1>
            </header>
            <main>
                <form onSubmit={handleSubmit}>
                    <input
                        type="text"
                        value={ticker}
                        onChange={(e) => setTicker(e.target.value)}
                        placeholder="Enter stock ticker (e.g., AAPL)"
                        required
                    />
                    <button type="submit" disabled={loading}>
                        {loading ? 'Analyzing...' : 'Analyze'}
                    </button>
                </form>

                {error && <p className="error">{error}</p>}

                {analysis && (
                    <div className="results">
                        <h2>Analysis for {ticker.toUpperCase()}</h2>
                        {analysis.arima_plot && (
                            <div dangerouslySetInnerHTML={{ __html: analysis.arima_plot }} />
                        )}
                        {analysis.sentiment !== null && (
                            <p>Sentiment: {analysis.sentiment}</p>
                        )}
                        {analysis.posts && (
                            <div>
                                <h3>Reddit Posts</h3>
                                <pre>{analysis.posts}</pre>
                            </div>
                        )}
                    </div>
                )}
            </main>
        </div>
    );
}

export default App;