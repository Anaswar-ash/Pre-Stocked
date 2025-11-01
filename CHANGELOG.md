# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-11-01

### Added
- `LICENSE` file (MIT License).
- `CONTRIBUTING.md` with contribution guidelines.
- `.editorconfig` for consistent coding styles.
- Unit tests for `api/analysis/lstm_model.py`.
- Unit tests for `api/analysis/sentiment.py`.
- GitHub Actions CI workflow for automated testing.

### Changed
- Improved `README.md` with new sections: "Technologies Used", "Project Structure", "Contributing", and "License".

## [0.1.0] - 2025-10-30

### Added
- Backtesting framework for ARIMA and LSTM models.
- API endpoint and Celery task to run backtesting.
- Backtesting page to the frontend to trigger backtesting and display results.

### Changed
- Generalized the forecasting functions in `arima_model.py` and `lstm_model.py` to be used in the backtesting framework.
