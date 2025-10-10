import React from 'react';

const AnalysisForm = ({ handleSubmit, ticker, setTicker, loading, setAnalysisType }) => (
    <form onSubmit={handleSubmit}>
        <input
            type="text"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            placeholder="Enter stock ticker (e.g., AAPL)"
            required
        />
        <button type="submit" disabled={loading} onClick={() => setAnalysisType('simple')}>
            {loading ? 'Analysing...' : 'Analyze'}
        </button>
        <button type="submit" disabled={loading} onClick={() => setAnalysisType('hybrid')}>
            {loading ? 'Analysing...' : 'Hybrid Analyze'}
        </button>
    </form>
);

export default AnalysisForm;
