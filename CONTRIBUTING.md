# Contributing to ShadowOps Digest

Thank you for your interest in contributing to ShadowOps Digest! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/shadowops-digest.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Set up your development environment (see README.md)

## Development Workflow

### Backend Development

1. Navigate to the backend directory: `cd backend`
2. Install dependencies: `pip install -r requirements.txt`
3. Run tests: `pytest`
4. Start the development server: `uvicorn main:app --reload`

### Frontend Development

1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Run tests: `npm test`
4. Start the development server: `npm start`

## Code Standards

### Python (Backend)

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions focused and single-purpose
- Add unit tests for new functionality

### JavaScript/React (Frontend)

- Use functional components with hooks
- Follow React best practices
- Use meaningful variable and function names
- Keep components small and reusable
- Add tests for new components

## Testing

- All new features must include tests
- Ensure all tests pass before submitting a PR
- Aim for meaningful test coverage, not just high percentages
- Test both happy paths and error cases

### Running Tests

**Backend:**
```bash
cd backend
pytest
pytest -v  # verbose output
```

**Frontend:**
```bash
cd frontend
npm test
npm test -- --coverage  # with coverage report
```

## Pull Request Process

1. Update documentation if you're changing functionality
2. Add tests for new features
3. Ensure all tests pass
4. Update the README.md if needed
5. Write a clear PR description explaining:
   - What changes you made
   - Why you made them
   - How to test them

## Commit Messages

Write clear, concise commit messages:

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- Reference issues and pull requests when relevant

Examples:
```
Add clustering algorithm for ticket categorization
Fix API endpoint validation for empty ticket lists
Update README with Docker setup instructions
```

## Code Review

All submissions require review. We use GitHub pull requests for this purpose. Reviewers will check for:

- Code quality and style
- Test coverage
- Documentation updates
- Performance implications
- Security considerations

## Questions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Questions about the codebase
- Suggestions for improvements

Thank you for contributing!
