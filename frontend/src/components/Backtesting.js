import React, { useState } from 'react';

function Backtesting() {
    const [ticker, setTicker] = useState('');
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [progress, setProgress] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setResults(null);
        setProgress('');

        const formData = new FormData();
        formData.append('ticker', ticker);

        try {
            const response = await fetch('/api/backtest', {
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
            }
        } catch (error) {
            setError('Failed to start backtesting. Please try again.');
            setLoading(false);
        }
    };

    const pollTaskStatus = (taskId) => {
        const startTime = Date.now();
        const timeout = 10 * 60 * 1000; // 10 minutes timeout

        const interval = setInterval(async () => {
            if (Date.now() - startTime > timeout) {
                clearInterval(interval);
                setError('Backtesting timed out. Please ensure backend services are running and try again.');
                setLoading(false);
                setProgress('');
                return;
            }

            try {
                const response = await fetch(`/status/${taskId}`);
                const data = await response.json();

                if (data.state === 'SUCCESS') {
                    clearInterval(interval);
                    setProgress('');
                    setResults(data.result.result);
                    setLoading(false);
                } else if (data.state === 'FAILURE') {
                    clearInterval(interval);
                    setError(data.status || 'Backtesting failed. Please try again.');
                    setLoading(false);
                    setProgress('');
                } else if (data.state === 'PROGRESS') {
                    setProgress(data.status);
                }

            } catch (error) {
                clearInterval(interval);
                setError('Failed to get backtesting status.');
                setLoading(false);
                setProgress('');
            }
        }, 5000);
    };

    return (
        <div>
            <h2>Backtesting</h2>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    value={ticker}
                    onChange={(e) => setTicker(e.target.value)}
                    placeholder="Enter stock ticker"
                    required
                />
                <button type="submit" disabled={loading}>
                    {loading ? 'Running...' : 'Run Backtesting'}
                </button>
            </form>

            {error && <p className="error-message">{error}</p>}
            {loading && <p>Loading...</p>}
            {progress && <p className="progress-message">{progress}</p>}

            {results && (
                <div className="results-display">
                    <h3>Backtesting Results for {ticker.toUpperCase()}</h3>
                    <div>
                        <h4>ARIMA Model</h4>
                        <p>Mean Absolute Error (MAE): {results.arima_mae.toFixed(4)}</p>
                        <p>Root Mean Squared Error (RMSE): {results.arima_rmse.toFixed(4)}</p>
                    </div>
                    <div>
                        <h4>LSTM Model</h4>
                        <p>Mean Absolute Error (MAE): {results.lstm_mae.toFixed(4)}</p>
                        <p>Root Mean Squared Error (RMSE): {results.lstm_rmse.toFixed(4)}</p>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Backtesting;
