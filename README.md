<h1 align="center">
    <img src="https://github.com/Znaxh/CodeSolAI/blob/main/images/codesolai_logo-png.png?raw=true" height="100" width="375" alt="banner" /><br>
</h1>

<p align="center">
  <img src="https://logos-world.net/wp-content/uploads/2023/07/Medium-Emblem.png" alt="Medium Logo" height="50" width="100"/>
</p>

# CodeSolAI

A fully autonomous agentic CLI tool for interacting with large language models, featuring sophisticated task decomposition, real-time progress tracking, and comprehensive file creation capabilities.

## Overview

CodeSolAI is an advanced command-line interface that transforms simple prompts into complex, multi-step autonomous executions. Built with a focus on developer productivity, it provides intelligent task breakdown, sequential execution, and robust file creation - making it ideal for rapid prototyping, project scaffolding, and automated development workflows.

## Key Features

### Autonomous Agent System
- **Intelligent Task Decomposition**: Automatically breaks down complex requests into manageable subtasks
- **Sequential Execution**: Executes tasks in logical order with dependency management
- **Real-Time Progress Tracking**: Visual progress bars, task status updates, and completion summaries
- **Comprehensive File Creation**: Creates complete, functional files with proper content (not placeholders)
- **Project Structure Generation**: Automatically creates proper directory structures and file hierarchies

### Advanced Features
- **Autonomous Mode**: Auto-approve actions for hands-free operation
- **Effort Levels**: Control reasoning complexity (low, medium, high, maximum)
- **Security Controls**: Path validation, command filtering, and sandbox mode
- **Intelligent Logging**: Minimal output by default, verbose debugging available
- **Error Handling**: Graceful fallbacks and user-friendly error messages

### Multi-Provider Support
- **Claude (Anthropic)**: Claude 3.5 Sonnet and Haiku models
- **Google Gemini**: Gemini Pro and Flash models
- **OpenAI GPT**: GPT-4 and GPT-3.5 models
- **Flexible Configuration**: Easy switching between providers and models

### Comprehensive Tool System
- **Filesystem Operations**: Read, write, create, delete, copy, move files and directories
- **Command Execution**: Run shell commands with security controls
- **Code Analysis**: Analyze code structure, complexity, and dependencies
- **Network Operations**: HTTP requests, file downloads, connectivity testing
- **18+ Specialized Tools**: Covering all common development tasks

## Installation

### Prerequisites
- Python 3.9 or higher
- Internet connection for API calls

### Install from PyPI
```bash
pip install codesolai
```

### Install with uv (Recommended)
```bash
uv add codesolai
```

### Install from Source
```bash
git clone https://github.com/Znaxh/codesolai.git
cd codesolai
pip install -e .
```

## Quick Start

### 1. Initial Setup
Run the interactive setup to configure your API keys:
```bash
codesolai --setup
```

### 2. Basic Usage
```bash
# Simple prompt
codesolai "Create a Python web scraper for news articles"

# Agent mode with specific provider
codesolai --agent --provider claude "Build a REST API with authentication"

# Autonomous mode for complex projects
codesolai --agent --autonomous "Create a full-stack web application with React and FastAPI"
```

### 3. Advanced Usage
```bash
# High effort reasoning with debug logging
codesolai --agent --autonomous --effort high --debug "Optimize this codebase for performance"

# Specific model and custom parameters
codesolai --provider gemini --model gemini-pro --temperature 0.3 "Explain quantum computing"

# Interactive chat mode
codesolai --interactive
```

## Command Line Options

```
Usage: codesolai [OPTIONS] [PROMPT]...

Options:
  -p, --provider TEXT             LLM provider (claude, gemini, gpt)
  -k, --api-key TEXT              API key for the provider
  -m, --model TEXT                Specific model to use (optional)
  --timeout INTEGER               Request timeout in milliseconds
  --max-tokens INTEGER            Maximum tokens in response
  --temperature FLOAT             Temperature for response generation
  --agent / --no-agent            Enable/disable agent mode
  --autonomous                    Enable autonomous multi-step execution
  --effort [low|medium|high|maximum]
                                  Reasoning effort level
  --max-iterations INTEGER        Maximum iterations for autonomous mode
  --debug                         Enable verbose debug logging
  --trace                         Enable execution tracing
  --config                        Show current configuration
  --config-example                Create example configuration file
  --config-reset                  Reset configuration to defaults
  --test-key                      Test API key validity
  --version                       Show version information
  --setup                         Run interactive setup
  -i, --interactive               Start interactive chat mode
  --help                          Show this message and exit.
```

## Configuration

CodeSolAI stores configuration in `~/.codesolairc`. You can manage settings using:

```bash
# View current configuration
codesolai --config

# Set values
codesolai config-set key value

# Reset to defaults
codesolai --config-reset
```

## Environment Variables

You can also configure CodeSolAI using environment variables:

```bash
export CLAUDE_API_KEY="sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export GPT_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export GEMINI_API_KEY="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

## Debugging and Logging

CodeSolAI uses intelligent logging that shows minimal output by default for a clean user experience:

```bash
# Normal operation (minimal logging)
codesolai --agent --autonomous "Set up a Flask web app"

# Enable verbose debug logging
codesolai --agent --autonomous --debug "Set up a Flask web app"

# Enable execution tracing for detailed analysis
codesolai --agent --autonomous --debug --trace "Set up a Flask web app"
```

**Logging Levels:**
- **Default**: Shows only essential progress and results
- **Debug**: Shows detailed system initialization and execution logs
- **Trace**: Includes complete execution traces and metrics

This design ensures that normal users see clean, focused output while developers can access detailed debugging information when needed.

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

# Project creation
codesolai --agent --autonomous "Create a Python package with proper structure"

# Code analysis
codesolai --agent "Analyze this codebase and suggest improvements"

# Web development
codesolai --agent --autonomous "Build a blog website with user authentication"

# Data processing
codesolai --agent "Create a data pipeline to process CSV files"
```

## Architecture

CodeSolAI is built with a modular architecture consisting of:

- **Core Agent System**: Sophisticated reasoning and execution engine
- **Provider Manager**: Multi-LLM provider abstraction layer
- **Tool Registry**: Extensible tool system with 18+ built-in tools
- **Task Manager**: Intelligent task decomposition and progress tracking
- **Context Manager**: Advanced context handling and memory management
- **Security Layer**: Comprehensive security controls and validation

For detailed architecture information, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/Znaxh/codesolai.git
cd codesolai

# Set up Python environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync

# Install development dependencies
uv add --dev pytest pytest-asyncio pytest-cov black isort mypy

# Run tests
pytest
```

### Code Quality

We use several tools to maintain code quality:

```bash
# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Run tests with coverage
pytest --cov=src/codesolai
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Guidelines

1. Follow the existing code style and patterns
2. Add tests for new functionality
3. Update documentation as needed
4. Ensure all tests pass before submitting

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [Installation Guide](INSTALL.md) | [Contributing Guide](CONTRIBUTING.md)
- **Issues**: [GitHub Issues](https://github.com/Znaxh/codesolai/issues)
- **Repository**: [GitHub Repository](https://github.com/Znaxh/codesolai)

## Acknowledgments

Built with modern Python tools and libraries:
- **Click**: Command-line interface framework
- **Rich**: Terminal UI and formatting
- **httpx**: Modern HTTP client
- **aiofiles**: Asynchronous file operations
