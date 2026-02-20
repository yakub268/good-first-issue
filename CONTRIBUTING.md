# Contributing to Good First Issue Finder

Thanks for your interest in contributing! This project aims to help new contributors find their first open source issues.

## Development Setup

1. Fork and clone the repo
2. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   ```
3. Install in dev mode:
   ```bash
   pip install -e ".[dev]"
   ```

## Running Tests

```bash
pytest tests/
```

## Code Style

This project uses:
- **Black** for formatting (`black gfi/`)
- **Ruff** for linting (`ruff check gfi/`)

Run before committing:
```bash
black gfi/ tests/
ruff check gfi/ tests/
```

## Ideas for Contributions

### Good First Issues
- Add support for GitLab issues
- Cache GitHub API responses to disk for faster reruns
- Add `gfi bookmark <url>` to save issues for later
- Export results to JSON/CSV
- Add color themes

### Medium Complexity
- Add GraphQL API support for faster profile analysis
- Implement smart retry with exponential backoff
- Add more scoring factors (e.g., "has reproduction repo")
- Filter by project topics/tags

### Advanced
- Machine learning model to predict issue quality
- Integration with GitHub CLI (`gh`)
- Watch mode that notifies when new matching issues appear
- Browser extension

## Pull Request Process

1. Create a feature branch (`git checkout -b feature/amazing-thing`)
2. Make your changes
3. Add tests if applicable
4. Run formatting and linting
5. Commit with clear message
6. Push and open a PR

## Questions?

Open an issue or reach out in Discussions.
