<h1 align="center">
    <img src="https://github.com/Znaxh/CodeSolAI/blob/main/images/codesolai_logo-png.png?raw=true" height="100" width="375" alt="banner" /><br>
</h1>

<p align="center">
  <a href="https://medium.com/@znaxxh/codesolai-7c78a050b759" target="_blank">
    <img src="https://logos-world.net/wp-content/uploads/2023/07/Medium-Emblem.png" alt="Medium Logo" height="50" width="100"/>
  </a>
</p>


# CodeSolAI

An intelligent command-line assistant that helps you build software projects through natural language conversations. Simply describe what you want to create, and CodeSolAI will automatically break down your request into tasks and execute them step by step.

## What is CodeSolAI?

CodeSolAI is like having an experienced developer assistant that can understand your project ideas and turn them into working code. Whether you're a beginner learning to code or an experienced developer looking to speed up your workflow, CodeSolAI can help you:

- **Create complete projects** from simple descriptions
- **Generate functional code** with proper structure and best practices
- **Set up development environments** automatically
- **Build web applications, APIs, scripts, and more** without writing code manually

Think of it as your personal coding assistant that never gets tired and always follows best practices.

## What Can CodeSolAI Do?

### For Beginners
- **Learn by Example**: See how real projects are structured and built
- **No Setup Hassle**: CodeSolAI handles all the configuration and dependencies
- **Instant Results**: Get working code immediately, then study how it works
- **Best Practices**: All generated code follows industry standards and conventions

### For Everyone
- **Smart Task Breaking**: Converts "build a website" into specific, actionable steps
- **Real-Time Progress**: Watch as your project comes together step by step
- **Complete Projects**: Creates fully functional applications, not just code snippets
- **Multiple Languages**: Works with Python, JavaScript, HTML/CSS, and more

### Supported AI Models
CodeSolAI works with the most advanced AI models available:
- **Claude (Anthropic)**: Excellent for complex reasoning and code generation
- **Google Gemini**: Fast and efficient for most development tasks
- **OpenAI GPT**: Reliable and well-tested for various programming languages

### Built-in Capabilities
CodeSolAI comes with everything needed for software development:
- **File Management**: Create, read, write, and organize project files
- **Code Execution**: Run and test your code automatically
- **Project Analysis**: Understand code structure and identify improvements
- **Web Operations**: Download resources and make API calls
- **Development Tools**: 18+ specialized tools for common programming tasks

## Getting Started

### Step 1: Check Your System
Before installing, make sure you have:
- **Python 3.9 or newer** (check with `python --version`)
- **Internet connection** (CodeSolAI needs to connect to AI services)

Don't have Python? Download it from [python.org](https://python.org) - it's free and easy to install.

### Step 2: Install CodeSolAI
Choose the method that works best for you:

**Option A: Simple Installation (Recommended for beginners)**
```bash
pip install codesolai
```

**Option B: Modern Python Package Manager**
```bash
uv add codesolai
```

**Option C: From Source Code (For developers)**
```bash
git clone https://github.com/Znaxh/codesolai.git
cd codesolai
pip install -e .
```

### Step 3: Get an AI API Key
CodeSolAI needs an API key to work with AI services. Choose one:

- **Claude (Recommended)**: Sign up at [console.anthropic.com](https://console.anthropic.com)
- **Google Gemini**: Get a key at [aistudio.google.com](https://aistudio.google.com)
- **OpenAI GPT**: Register at [platform.openai.com](https://platform.openai.com)

Most services offer free credits to get started.

## Your First Project

### Step 1: Set Up Your API Key
After installation, run this command to configure CodeSolAI:
```bash
codesolai --setup
```
This will guide you through adding your API key. You only need to do this once.

### Step 2: Create Your First Project
Let's start with something simple. Try this command:
```bash
codesolai --agent --autonomous "Create a simple Python calculator that can add, subtract, multiply, and divide"
```

Watch as CodeSolAI:
1. Breaks down your request into specific tasks
2. Creates the necessary files and folders
3. Writes the Python code
4. Tests the calculator to make sure it works

### Step 3: Try More Examples

**Build a Website**
```bash
codesolai --agent --autonomous "Create a personal portfolio website with HTML and CSS"
```

**Make a Web API**
```bash
codesolai --agent --autonomous "Build a simple REST API for a todo list using Python Flask"
```

**Data Analysis Script**
```bash
codesolai --agent --autonomous "Create a Python script that analyzes CSV data and creates charts"
```

**Interactive Mode**
For back-and-forth conversations:
```bash
codesolai --interactive
```

### Understanding the Commands

- `--agent`: Enables smart task planning and execution
- `--autonomous`: Lets CodeSolAI work independently without asking for permission
- `--provider claude`: Specifies which AI service to use (claude, gemini, or gpt)
- `--interactive`: Starts a chat-like conversation mode

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
