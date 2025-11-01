# Contributing to Pre-Stocked

First off, thank you for considering contributing to Pre-Stocked! It's people like you that make the open source community such a great place.

## How Can I Contribute?

### Reporting Bugs

If you find a bug, please open an issue on our GitHub repository. Please include as much detail as possible, including:

*   A clear and descriptive title.
*   A step-by-step description of how to reproduce the bug.
*   The expected behavior and what actually happened.
*   Your operating system, browser, and any other relevant information.

### Suggesting Enhancements

If you have an idea for a new feature or an improvement to an existing one, please open an issue on our GitHub repository. Please include:

*   A clear and descriptive title.
*   A detailed description of the proposed enhancement.
*   Any mockups or examples that might help illustrate your idea.

### Pull Requests

We welcome pull requests! If you'd like to contribute code, please follow these steps:

1.  Fork the repository and create a new branch from `main`.
2.  Make your changes and ensure that the code lints and tests pass.
3.  Open a pull request with a clear and descriptive title and a detailed description of your changes.

## Styleguides

### Git Commit Messages

*   Use the present tense ("Add feature" not "Added feature").
*   Use the imperative mood ("Move cursor to..." not "Moves cursor to...").
*   Limit the first line to 72 characters or less.
*   Reference issues and pull requests liberally after the first line.

### Python Styleguide

We follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for Python code.

### JavaScript Styleguide

We follow the [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript).

## Known Issues

*   **UI/UX Polish:** While functional and improved with Bootstrap, the UI could benefit from a more thoughtful design, including better spacing, typography, and a more distinct visual identity.
*   **Error Handling Granularity:** While custom exceptions are used, the frontend could do a better job of displaying user-friendly error messages for specific failure modes (e.g., "Invalid stock ticker" vs. a generic "Analysis failed").

## Future Improvements

*   **Enhance Test Suite:** Prioritize writing unit tests for the `hybrid_analysis.py` module, mocking the TensorFlow/Keras and Transformers libraries to isolate the logic.
*   **Refactor Configuration:** Move hardcoded parameters from the analysis modules into the Flask application's configuration.
*   **Containerize the Application:** Create a `Dockerfile` for the backend and a `docker-compose.yml` file to orchestrate the entire application stack (Flask, React, Redis, Celery, PostgreSQL). This will simplify the local setup process and prepare the application for deployment.
