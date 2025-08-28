<h1 align="center">
    <img src="https://github.com/Znaxh/codesolai/blob/main/images/codesolai_logo-png.png?raw=true" height="100" width="375" alt="banner" /><br>
</h1>

<div align="center">
<a href="https://medium.com/@znaxxh/codesolai-7c78a050b759">
  <img 
    src="https://logos-world.net/wp-content/uploads/2023/07/Medium-Emblem.png" 
    alt="Medium Logo" 
    height="50" 
    width="100" 
    style="object-fit: cover; object-position: center; border-radius: 5px; border: 2px solid white;"
  />
</a>
</div>


# CodeSolAI

**CodeSolAI** is a fully autonomous agentic CLI tool for interacting with large language models (LLMs) like Claude, Gemini, and GPT. It provides both simple chat interactions and sophisticated agent capabilities for autonomous task execution with advanced task decomposition, sequential execution, and comprehensive project creation capabilities.

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

### Enhanced Autonomous System
- **Intelligent Task Decomposition**: Automatically breaks complex requests into manageable subtasks
- **Sequential Task Execution**: Executes tasks in logical order with dependency management
- **Template-Based Project Creation**: Pre-built templates for common project types (Flask web apps, FastAPI, React apps)
- **Real-Time Progress Tracking**: Visual progress bars, task status updates, and completion summaries
- **Comprehensive File Creation**: Creates complete, functional files with proper content (not placeholders)
- **Project Structure Generation**: Automatically creates proper directory structures and file hierarchies

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

### Enhanced Autonomous Mode

The enhanced autonomous mode is the most powerful feature of CodeSolAI, providing complete project creation with minimal user input:

```bash
# Create a complete Flask web application
codesolai --agent --autonomous "Set up a Flask web app with authentication"

# Build a REST API with database
codesolai --agent --autonomous "Create a FastAPI service with user management and SQLite database"

# Generate a full-stack application
codesolai --agent --autonomous "Build a React frontend with Python backend for a todo application"

# Set up a data processing pipeline
codesolai --agent --autonomous "Create a Python project for processing CSV files with pandas"
```

**What happens during autonomous execution:**

1. **Analysis**: Request is analyzed and project type is detected
2. **Planning**: Complex request is broken down into 8+ specific tasks
3. **Execution**: Tasks are executed sequentially with real-time progress updates
4. **Creation**: Complete, functional files are created (not placeholders)
5. **Summary**: Comprehensive report shows all work completed and next steps

**Example output for Flask app creation:**
- `app.py` (3,135 bytes) - Complete Flask application with authentication
- `requirements.txt` - All necessary dependencies
- `templates/` directory with 5 HTML files (base, index, login, register, dashboard)
- Database initialization and user management code
- Session handling and password hashing
- Ready-to-run application with proper structure

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

## Enhanced Autonomous Mode

The enhanced autonomous mode provides sophisticated task management capabilities similar to advanced AI coding assistants, with automatic task decomposition and sequential execution.

### Key Capabilities

**Intelligent Task Management**
- Automatically decomposes complex requests into 8+ manageable subtasks
- Executes tasks sequentially with proper dependency management
- Provides real-time progress tracking with visual indicators
- Generates comprehensive completion summaries

**Complete Project Creation**
- Creates functional files with complete implementations (not placeholders)
- Generates proper directory structures and file hierarchies
- Uses pre-built templates for common project types
- Supports Flask web applications, FastAPI services, and more

**Advanced Progress Tracking**
- Visual progress bars showing task completion status
- Real-time task status updates and execution summaries
- Detailed logging of all actions and file operations
- Comprehensive reports of work completed

### Usage Examples

```bash
# Create complete web applications with authentication
codesolai --agent --autonomous "Set up a Flask web app with authentication"

# Build REST APIs with database integration
codesolai --agent --autonomous "Create a Python REST API with FastAPI and database"

# Generate complete project structures
codesolai --agent --autonomous "Build a React todo app with backend"

# Code analysis and documentation generation
codesolai --agent --autonomous "Analyze all Python files in src/ and create documentation"

# Development workflow automation
codesolai --agent --autonomous "Set up a new Python project with testing and CI/CD"
```

### Supported Project Types

**Flask Web Applications**
- Complete authentication system (registration, login, logout)
- Database integration with SQLite
- HTML templates with responsive design
- Session management and password hashing
- Proper project structure with templates and static files

**FastAPI Services**
- RESTful API endpoints with proper routing
- Database models and migrations
- Authentication and authorization
- API documentation with Swagger/OpenAPI
- Dependency injection and middleware setup

**Python Projects**
- Virtual environment setup
- Package structure with proper imports
- Testing framework configuration
- Documentation generation
- CI/CD pipeline setup

## Architecture

### Core Components

**Enhanced Agent System**
- `EnhancedAgent`: Main orchestrator for autonomous task execution
- `TaskManager`: Handles task decomposition, execution, and progress tracking
- `FileCreationHelper`: Contains templates and handles complete file generation
- `ToolRegistry`: Manages 18+ specialized tools for various operations

**Provider Integration**
- `ProviderManager`: Unified interface for multiple LLM providers
- `ClaudeProvider`: Integration with Anthropic's Claude models
- `GeminiProvider`: Integration with Google's Gemini models
- `GPTProvider`: Integration with OpenAI's GPT models

**Tool System**
- `FilesystemTool`: File and directory operations
- `ExecutionTool`: Safe command execution with filtering
- `NetworkTool`: HTTP requests and API interactions
- `AnalysisTool`: Code analysis and documentation generation

### Task Execution Flow

1. **Request Analysis**: Parse user input and detect project type
2. **Task Decomposition**: Break complex requests into subtasks
3. **Template Selection**: Choose appropriate templates for known project types
4. **Sequential Execution**: Execute tasks in dependency order
5. **Progress Tracking**: Provide real-time status updates
6. **Completion Summary**: Generate comprehensive execution report

## Use Cases

### Software Development
- **Project Scaffolding**: Create complete project structures with proper organization
- **Code Generation**: Generate functional code with complete implementations
- **Documentation**: Create comprehensive project documentation and API docs
- **Testing**: Set up testing frameworks and generate test suites
- **Refactoring**: Modernize legacy code with current best practices

### DevOps and Infrastructure
- **Configuration Management**: Create and manage deployment configurations
- **CI/CD Pipeline Setup**: Build automated testing and deployment workflows
- **Monitoring Setup**: Configure monitoring and alerting systems
- **Security Auditing**: Analyze code and configurations for security vulnerabilities
- **Infrastructure as Code**: Generate Terraform, Docker, and Kubernetes configurations

### Data and Analysis
- **Data Processing**: Batch process and transform large datasets
- **Report Generation**: Create automated reports with visualizations
- **API Development**: Build data APIs with proper validation and documentation
- **Database Setup**: Configure databases with proper schemas and migrations
- **ETL Pipelines**: Create data extraction, transformation, and loading workflows

## Technical Specifications

### Enhanced Autonomous System

**Task Management**
- Intelligent project type detection (Flask, FastAPI, React, etc.)
- Template-based task generation for known project types
- Dynamic task decomposition using AI for complex requests
- Sequential execution with dependency resolution
- Real-time progress tracking with visual indicators

**File Creation System**
- Complete, functional file templates (not placeholders)
- Automatic directory structure generation
- Content validation and quality assurance
- Support for multiple programming languages and frameworks
- Extensible template system for custom project types

**Progress Tracking**
- Visual progress bars with completion percentages
- Task-by-task status updates and timing information
- Comprehensive execution summaries with file listings
- Error reporting with detailed context and suggestions
- Success metrics and performance analytics

### Performance

CodeSolAI is designed for efficiency and reliability:

- **Response Time**: 1-3 seconds for most operations, 10-30 seconds for complex project creation
- **Concurrent Operations**: Supports multiple simultaneous tool executions
- **Memory Efficient**: Optimized for minimal resource usage with intelligent context management
- **Error Recovery**: Robust error handling with automatic retries and graceful degradation
- **Scalable**: Handles projects of any size with efficient resource allocation

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
