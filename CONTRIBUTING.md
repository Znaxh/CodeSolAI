# Contributing to CodeSolAI

Thank you for your interest in contributing to CodeSolAI! This document provides guidelines and information for contributors.

## 🚀 Quick Start

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Znaxh/codesolai.git
   cd codesolai
   ```

2. **Set up Python environment**
   ```bash
   # Using uv (recommended)
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv sync
   
   # Or using pip
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

3. **Install development dependencies**
   ```bash
   uv add --dev pytest pytest-asyncio pytest-cov black isort mypy pre-commit
   ```

4. **Run tests**
   ```bash
   pytest
   ```

## 📋 Development Guidelines

### Code Style

We use several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking
- **pytest**: Testing

Run all checks:
```bash
# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Run tests
pytest --cov=src/codesolai
```

### Project Structure

```
codesolai/
├── src/codesolai/           # Main package
│   ├── __init__.py
│   ├── cli.py               # CLI interface
│   ├── config.py            # Configuration management
│   ├── utils.py             # Utility functions
│   ├── setup.py             # Setup wizard
│   ├── interactive_session.py  # Interactive mode
│   ├── spinner_manager.py   # Loading animations
│   ├── providers/           # LLM providers
│   │   ├── __init__.py
│   │   ├── base_provider.py
│   │   ├── provider_manager.py
│   │   ├── claude_provider.py
│   │   ├── gpt_provider.py
│   │   └── gemini_provider.py
│   ├── core/               # Agent system (future)
│   └── tools/              # Tool system (future)
├── tests/                  # Test suite
├── docs/                   # Documentation
├── pyproject.toml          # Project configuration
└── README.md
```

## 🔧 Contributing Areas

### High Priority
- **Agent System**: Implement autonomous task execution
- **Tool System**: File operations, command execution
- **Test Suite**: Comprehensive testing framework
- **Documentation**: API docs, tutorials, examples

### Medium Priority
- **Streaming Responses**: Real-time response streaming
- **Function Calling**: Structured tool usage
- **Plugin System**: Extensible architecture
- **Performance**: Optimization and caching

### Low Priority
- **UI Improvements**: Better terminal interface
- **Configuration**: Advanced settings
- **Monitoring**: Usage analytics and metrics

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/codesolai --cov-report=html

# Run specific test file
pytest tests/test_providers.py

# Run with verbose output
pytest -v
```

### Writing Tests
- Place tests in the `tests/` directory
- Use descriptive test names: `test_claude_provider_handles_api_errors`
- Mock external API calls
- Test both success and error cases
- Include async tests for async functions

Example test:
```python
import pytest
from unittest.mock import AsyncMock, patch
from codesolai.providers.claude_provider import ClaudeProvider

@pytest.mark.asyncio
async def test_claude_provider_successful_call():
    provider = ClaudeProvider()
    
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            'content': [{'text': 'Hello, world!'}]
        }
        mock_post.return_value = mock_response
        
        result = await provider.call('test-key', 'Hello')
        assert result == 'Hello, world!'
```

## 📝 Pull Request Process

1. **Fork the repository** and create a feature branch
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding guidelines

3. **Add tests** for new functionality

4. **Update documentation** if needed

5. **Run the full test suite**
   ```bash
   pytest
   black src/ tests/
   isort src/ tests/
   mypy src/
   ```

6. **Commit your changes** with clear messages
   ```bash
   git commit -m "feat: add streaming response support"
   ```

7. **Push to your fork** and create a pull request

### Commit Message Format
We follow conventional commits:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `style:` Code style changes
- `chore:` Maintenance tasks

## 🐛 Bug Reports

When reporting bugs, please include:
- **Environment**: Python version, OS, CodeSolAI version
- **Steps to reproduce**: Clear, minimal example
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Error messages**: Full stack traces if applicable

## 💡 Feature Requests

For feature requests:
- **Use case**: Why is this feature needed?
- **Proposed solution**: How should it work?
- **Alternatives**: Other approaches considered
- **Implementation**: Any implementation ideas

## 📚 Documentation

Help improve documentation:
- **README**: Keep examples current
- **API docs**: Document new functions/classes
- **Tutorials**: Step-by-step guides
- **Examples**: Real-world use cases

## 🤝 Community

- **Be respectful**: Follow the code of conduct
- **Be helpful**: Assist other contributors
- **Be patient**: Reviews take time
- **Be collaborative**: Work together on solutions

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## ❓ Questions

If you have questions:
- Check existing issues and discussions
- Create a new issue with the "question" label
- Join our community discussions

Thank you for contributing to CodeSolAI! 🎉
