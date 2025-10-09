import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
    const [ticker, setTicker] = useState('');
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [analysisType, setAnalysisType] = useState('simple');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setAnalysis(null);

        const formData = new FormData();
        formData.append('ticker', ticker);
        formData.append('analysis_type', analysisType);

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
            let url = analysisType === 'simple' ? `/data/${ticker}` : `/hybrid_data/${ticker}`;
            const response = await fetch(url);
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
                    <button type="submit" disabled={loading} onClick={() => setAnalysisType('simple')}>
                        {loading && analysisType === 'simple' ? 'Analyzing...' : 'Analyze'}
                    </button>
                    <button type="submit" disabled={loading} onClick={() => setAnalysisType('hybrid')}>
                        {loading && analysisType === 'hybrid' ? 'Analyzing...' : 'Hybrid Analyze'}
                    </button>
                </form>

                {error && <p className="error">{error}</p>}

                {analysis && (
                    <div className="results">
                        <h2>Analysis for {ticker.toUpperCase()}</h2>
                        {analysis.arima_plot && (
                            <div dangerouslySetInnerHTML={{ __html: analysis.arima_plot }} />
                        )}
                        {analysis.hybrid_plot && (
                            <div dangerouslySetInnerHTML={{ __html: analysis.hybrid_plot }} />
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