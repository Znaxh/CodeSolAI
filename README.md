# CodeSolAI

A powerful and user-friendly command-line interface for interacting with Large Language Models (Claude, Gemini, GPT). Get AI assistance directly in your terminal with an interactive conversational experience.

## 🚀 Quick Start

### 1. Install
```bash
pip install codesolai
```

### 2. Setup (Interactive)
```bash
codesolai setup
```
This will guide you through:
- Choosing your preferred AI provider
- Setting up your API key
- Configuring default settings

### 3. Start Using

#### Interactive Mode (Recommended)
```bash
# Start interactive conversation
codesolai

# Or explicitly use interactive command
codesolai interactive
```

#### Direct Commands
```bash
# Simple question
codesolai "Explain quantum computing"

# Pipe input
echo "Review this code for bugs" | codesolai

# Use specific provider
codesolai --provider gpt "Write a Python function to sort a list"
```

That's it! 🎉

## 📖 Usage

### Interactive Mode

The interactive mode provides a modern conversational experience with:
- **Persistent conversations** - Your chat history is saved and can be resumed
- **Rich formatting** - Syntax highlighting, tables, and beautiful output
- **Smart context** - The AI remembers your conversation context
- **Easy commands** - Type `/help` to see available commands

### Agent Mode

Enable autonomous agent capabilities for complex multi-step tasks:

```bash
# Enable agent mode for sophisticated reasoning
codesolai --agent "Create a Python web scraper for news articles"

# Autonomous mode for fully automated execution
codesolai --autonomous "Set up a complete Flask API with database"
```

### Configuration

```bash
# View current configuration
codesolai config-show

# Set default provider
codesolai config-set --set-provider claude

# Set API key
codesolai config-set --set-api-key sk-ant-xxx --set-provider claude

# Enable agent mode by default
codesolai config-set --set-agent-enabled true
```

## 🤖 Supported Providers

- **Claude (Anthropic)** - Advanced reasoning and analysis
- **GPT (OpenAI)** - Creative and versatile responses  
- **Gemini (Google)** - Multimodal capabilities

## 🛠️ Features

- **Interactive Chat Mode** - Persistent conversations with rich formatting
- **Agent Mode** - Autonomous task execution with tool usage
- **Multiple Providers** - Support for Claude, GPT, and Gemini
- **Configuration Management** - Easy setup and customization
- **Pipe Support** - Use with other command-line tools
- **Rich Output** - Beautiful formatting with syntax highlighting

## 📋 Requirements

- Python 3.9+
- API key for at least one supported provider

## 🔧 Development

This project is converted from the original Node.js visaire-cli to Python for better integration with Python development workflows.

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
# codesolai
