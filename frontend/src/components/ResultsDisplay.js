import React from 'react';

const ResultsDisplay = ({ analysis, ticker }) => (
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
);

export default ResultsDisplay;
