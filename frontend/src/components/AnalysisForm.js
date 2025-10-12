import React from 'react';

const AnalysisForm = ({ handleSubmit, ticker, setTicker, loading, setAnalysisType }) => (
    <form onSubmit={handleSubmit} className="mb-4">
        <div className="form-group">
            <input
                type="text"
                className="form-control"
                value={ticker}
                onChange={(e) => setTicker(e.target.value)}
                placeholder="Enter stock ticker (e.g., AAPL)"
                required
            />
        </div>
        <button type="submit" className="btn btn-primary mr-2" disabled={loading} onClick={() => setAnalysisType('simple')}>
            {loading ? 'Analysing...' : 'Analyze'}
        </button>
        <button type="submit" className="btn btn-secondary" disabled={loading} onClick={() => setAnalysisType('hybrid')}>
            {loading ? 'Analysing...' : 'Hybrid Analyze'}
        </button>
    </form>
);

export default AnalysisForm;
