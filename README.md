<h1 align="center">
    <img src="https://github.com/Znaxh/codesolai/blob/main/images/codesolai_logo-png.png?raw=true" height="100" width="375" alt="banner" /><br>
</h1>

<div align="center">

[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Znaxh/codesolai)
<a href="https://medium.com/@znaxxh/codesolai-7c78a050b759">
  <img src="https://cdn.worldvectorlogo.com/logos/wordmark-white-medium.svg" alt="Medium Logo" width="100"/>
</a>
</div>


# CodeSolAI

**CodeSolAI** is a fully autonomous agentic CLI tool for interacting with large language models (LLMs) like Claude, Gemini, and GPT. It provides both simple chat interactions and sophisticated agent capabilities for autonomous task execution.

## Features

### Core Functionality
- **Multi-Provider Support**: Works with Claude (Anthropic), Gemini (Google), and GPT (OpenAI)
- **Interactive Chat Mode**: Real-time conversations with your chosen LLM
- **Agent System**: Autonomous task execution with tool integration
- **Rich Terminal UI**: Beautiful spinners, formatting, and user experience
- **Configuration Management**: Easy setup and persistent settings

### Agent Capabilities
- **File Operations**: Read, write, create, and manage files
- **Code Analysis**: Analyze code structure and provide insights
- **Command Execution**: Execute shell commands safely
- **Network Operations**: Make HTTP requests and API calls
- **Multi-step Planning**: Break down complex tasks into executable steps
- **Tool Integration**: 18+ specialized tools for various tasks

### Advanced Features
- **Autonomous Mode**: Auto-approve actions for hands-free operation
- **Effort Levels**: Control reasoning complexity (low, medium, high, maximum)
- **Security Controls**: Path validation, command filtering, and sandbox mode
- **Comprehensive Logging**: Detailed logs with metrics and tracing
- **Error Handling**: Graceful fallbacks and user-friendly error messages

## Quick Start

### Installation

```bash
# Install from PyPI (when published)
pip install codesolai

# Or install from source
git clone https://github.com/Znaxh/codesolai.git
cd codesolai
uv install
```

### Setup

```bash
# Run interactive setup
codesolai --setup

# Or configure manually
codesolai config-set defaultProvider claude
codesolai config-set claude.apiKey your-api-key-here
```

### Basic Usage

```bash
# Simple chat
codesolai "Hello, how are you?"

# Interactive mode
codesolai --interactive

# Agent mode with file operations
codesolai --agent "List files in current directory"

# Autonomous mode (auto-approve actions)
codesolai --agent --autonomous "Create a Python script that prints hello world"
```

## Documentation

### Command Line Options

```
Usage: codesolai [OPTIONS] [PROMPT]...

Options:
  -p, --provider TEXT             LLM provider (claude, gemini, gpt)
  -k, --api-key TEXT              API key for the provider
  -m, --model TEXT                Model to use
  -t, --temperature FLOAT         Response creativity (0.0-1.0)
  --max-tokens INTEGER            Maximum response length
  --timeout INTEGER               Request timeout in seconds
  --retries INTEGER               Number of retry attempts
  --output-format [text|json]     Output format
  --agent / --no-agent            Enable/disable agent mode
  --autonomous                    Enable autonomous multi-step execution
  --effort [low|medium|high|maximum]  Reasoning effort level
  --max-iterations INTEGER        Maximum iterations for autonomous mode
  --setup                         Run interactive setup
  --config                        Show current configuration
  --config-example                Create example configuration file
  --config-reset                  Reset configuration to defaults
  --test-key                      Test API key validity
  --version                       Show version information
  --interactive, -i               Start interactive chat mode
  --help                          Show this message and exit.
```

### Configuration

CodeSolAI stores configuration in `~/.codesolairc`. You can manage settings using:

```bash
# View current configuration
codesolai --config

# Set values
codesolai config-set key value

# Reset to defaults
codesolai --config-reset
```

### Environment Variables

You can also configure CodeSolAI using environment variables:

```bash
export CLAUDE_API_KEY="sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export GPT_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export GEMINI_API_KEY="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

## Agent System

The agent system enables CodeSolAI to perform complex, multi-step tasks autonomously:

### Available Tools

- **Filesystem**: Read, write, list, create files and directories
- **Execution**: Run shell commands and scripts
- **Analysis**: Analyze code structure and dependencies
- **Network**: Make HTTP requests and API calls
- **And more**: 18+ specialized tools for various tasks

### Agent Examples

```bash
# File operations
codesolai --agent "Read the README.md file and summarize it"

# Code analysis
codesolai --agent "Analyze the Python files in src/ directory"

# Multi-step tasks
codesolai --agent --autonomous "Create a new Python project with proper structure"

# Development workflow
codesolai --agent "Run tests and create a summary report"
```

### Security Features

- **Path Validation**: Restricts file operations to allowed directories
- **Command Filtering**: Blocks dangerous commands (rm -rf, sudo, etc.)
- **Sandbox Mode**: Optional isolation for enhanced security
- **User Confirmation**: Requires approval for sensitive operations (unless autonomous)

## Development

### Requirements

- Python 3.8+
- uv (recommended) or pip

### Setup Development Environment

```bash
git clone https://github.com/Znaxh/codesolai.git
cd codesolai

# Install dependencies
uv install

# Run tests
uv run pytest

# Run with development code
uv run codesolai --help
```

### Testing

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_cli.py

# Run with coverage
uv run pytest --cov=codesolai
```

## Examples

### Simple Chat

```bash
$ codesolai "Explain quantum computing"
Quantum computing is a revolutionary approach to computation that leverages quantum
mechanical phenomena to process information in fundamentally different ways than
classical computers...
```

### Interactive Mode

```bash
$ codesolai --interactive
CodeSolAI Interactive Mode - Type '/help' for commands, '/exit' to quit

You: Hello!
AI: Hello! How can I help you today?

You: Write a Python function to calculate fibonacci numbers
AI: Here's a Python function to calculate Fibonacci numbers:

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

You: /exit
Goodbye!
```

### Agent File Operations

```bash
$ codesolai --agent "List files and create a summary"
Agent processing...
Agent completed 2 actions in 3s

I'll list the files in the current directory and create a summary for you.

Directory listing for /home/user/project:
  README.md
  src/
  tests/
  pyproject.toml
  LICENSE

Created summary.txt with project overview including 4 files and 2 directories.

Agent Actions Executed:
  1. list_directory
  2. write_file (summary.txt)
```

### Advanced Agent Usage

```bash
# Code analysis and documentation
$ codesolai --agent --autonomous "Analyze all Python files in src/ and create documentation"

# Project setup
$ codesolai --agent "Create a new Flask web application with proper structure"

# Development workflow
$ codesolai --agent "Run the test suite and generate a coverage report"

# File processing
$ codesolai --agent "Convert all .txt files in docs/ to markdown format"
```

## Use Cases

### For Developers
- **Code Review**: Analyze code quality and suggest improvements
- **Documentation**: Generate comprehensive project documentation
- **Testing**: Create and run test suites automatically
- **Refactoring**: Modernize legacy code with best practices
- **API Integration**: Build integrations with external services

### For DevOps
- **Infrastructure**: Analyze and optimize deployment configurations
- **Monitoring**: Create monitoring and alerting setups
- **Automation**: Build CI/CD pipelines and automation scripts
- **Security**: Audit code and configurations for security issues

### For Data Analysis
- **File Processing**: Batch process and transform data files
- **Report Generation**: Create automated reports from data
- **Data Validation**: Verify data integrity and format compliance
- **Visualization**: Generate charts and graphs from datasets

## Performance

CodeSolAI is designed for efficiency and reliability:

- **Response Time**: 1-3 seconds for most operations
- **Concurrent Operations**: Supports multiple simultaneous tool executions
- **Memory Efficient**: Optimized for minimal resource usage
- **Error Recovery**: Robust error handling with automatic retries
- **Scalable**: Handles projects of any size

## Security

Security is a top priority in CodeSolAI:

### Built-in Protections
- **Path Validation**: Restricts file access to authorized directories
- **Command Filtering**: Blocks potentially dangerous system commands
- **API Key Protection**: Secure handling and storage of credentials
- **Sandbox Mode**: Optional isolation for enhanced security
- **Audit Logging**: Comprehensive logging of all operations

### Best Practices
- Store API keys in environment variables or secure configuration
- Use the `--autonomous` flag only in trusted environments
- Regularly review and update allowed paths and commands
- Monitor logs for unusual activity

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- **Repository**: https://github.com/Znaxh/codesolai
- **Issues**: https://github.com/Znaxh/codesolai/issues
- **Documentation**: [INSTALL.md](INSTALL.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

## Acknowledgments

- Built with Python and modern async/await patterns
- Powered by leading LLM providers (Anthropic, Google, OpenAI)
- Inspired by the need for autonomous AI development tools
- Thanks to the open-source community for excellent libraries

---

**CodeSolAI** - Autonomous AI for developers, by developers.
