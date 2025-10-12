import React from 'react';

const ResultsDisplay = ({ analysis, ticker }) => (
    <div className="card">
        <div className="card-header">
            <h2>Analysis for {ticker.toUpperCase()}</h2>
        </div>
        <div className="card-body">
            {analysis.arima_plot && (
                <div dangerouslySetInnerHTML={{ __html: analysis.arima_plot }} />
            )}
            {analysis.hybrid_plot && (
                <div dangerouslySetInnerHTML={{ __html: analysis.hybrid_plot }} />
            )}
            {analysis.sentiment !== null && (
                <p className="card-text">Sentiment: {analysis.sentiment}</p>
            )}
            {analysis.posts && (
                <div>
                    <h3>Reddit Posts</h3>
                    <div className="table-responsive">
                        <table className="table table-bordered">
                            <thead>
                                <tr>
                                    <th>Title</th>
                                    <th>Score</th>
                                    <th>Sentiment</th>
                                </tr>
                            </thead>
                            <tbody>
                                {analysis.posts.map((post, index) => (
                                    <tr key={index}>
                                        <td><a href={post.url} target="_blank" rel="noopener noreferrer">{post.title}</a></td>
                                        <td>{post.score}</td>
                                        <td>{post.sentiment}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    </div>
);

export default ResultsDisplay;
