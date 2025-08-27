# Installation Guide

This guide covers different ways to install and set up CodeSolAI.

## 📦 Installation Methods

### Method 1: pip (Recommended)

```bash
pip install codesolai
```

### Method 2: uv (Modern Python Package Manager)

```bash
uv add codesolai
```

### Method 3: From Source

```bash
git clone https://github.com/Znaxh/codesolai.git
cd codesolai
pip install -e .
```

### Method 4: From Wheel

```bash
# Download the latest wheel from releases
pip install codesolai-1.0.0-py3-none-any.whl
```

## 🔧 Requirements

- **Python**: 3.9 or higher
- **Operating System**: Windows, macOS, Linux
- **Internet Connection**: Required for API calls

## ⚡ Quick Setup

After installation, run the interactive setup:

```bash
codesolai --setup
```

This will guide you through:
1. Choosing your preferred AI provider
2. Setting up your API key
3. Configuring default settings

## 🔑 API Key Setup

### Option 1: Interactive Setup (Recommended)
```bash
codesolai --setup
```

### Option 2: Environment Variables
```bash
# For Claude (Anthropic)
export CLAUDE_API_KEY="sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# For GPT (OpenAI)
export GPT_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# For Gemini (Google)
export GEMINI_API_KEY="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### Option 3: Configuration File
Create `~/.codesolairc`:
```json
{
  "defaultProvider": "claude",
  "apiKeys": {
    "claude": "sk-ant-your-key-here",
    "gpt": "sk-your-key-here",
    "gemini": "your-key-here"
  }
}
```

## 🧪 Verify Installation

Test that everything works:

```bash
# Check version
codesolai --version

# Test configuration
codesolai --config

# Test API key (if configured)
codesolai --test-key

# Simple test
codesolai "Hello, how are you?"
```

## 🚀 Getting Started

### Basic Usage
```bash
# Simple question
codesolai "Explain quantum computing"

# Pipe input
echo "Review this code" | codesolai

# Interactive mode
codesolai --interactive
```

### Configuration
```bash
# Show current settings
codesolai --config

# Create example config
codesolai --config-example
```

## 🐛 Troubleshooting

### Common Issues

#### "codesolai: command not found"
- **Solution**: Make sure the installation directory is in your PATH
- **Check**: `pip show codesolai` to see installation location
- **Fix**: Add `~/.local/bin` to PATH or use full path

#### "No module named 'codesolai'"
- **Solution**: Install in the correct Python environment
- **Check**: `python -m pip list | grep codesolai`
- **Fix**: Reinstall with `pip install --user codesolai`

#### "Invalid API key format"
- **Solution**: Check your API key format
- **Claude**: Should start with `sk-ant-`
- **GPT**: Should start with `sk-`
- **Gemini**: Usually 39 characters, no prefix

#### "Rate limit exceeded"
- **Solution**: Wait before making more requests
- **Check**: Your API usage limits
- **Fix**: Upgrade your API plan if needed

### Getting Help

If you encounter issues:

1. **Check the documentation**: README.md and this guide
2. **Search existing issues**: GitHub issues page
3. **Create a new issue**: Include error messages and environment details
4. **Join discussions**: GitHub discussions for questions

### Environment Information

When reporting issues, include:

```bash
# System information
python --version
pip --version
codesolai --version

# Package information
pip show codesolai

# Configuration
codesolai --config
```

## 🔄 Updating

### Update to Latest Version
```bash
pip install --upgrade codesolai
```

### Check for Updates
```bash
pip list --outdated | grep codesolai
```

## 🗑️ Uninstallation

```bash
# Remove package
pip uninstall codesolai

# Remove configuration (optional)
rm ~/.codesolairc
rm ~/.codesolairc.example
```

## 🌐 Platform-Specific Notes

### Windows
- Use Command Prompt or PowerShell
- Path separator is `\` instead of `/`
- Config file location: `%USERPROFILE%\.codesolairc`

### macOS
- May need to use `python3` and `pip3`
- Config file location: `~/.codesolairc`
- Consider using Homebrew for Python

### Linux
- Usually works out of the box
- May need `--user` flag for pip
- Config file location: `~/.codesolairc`

## 🔒 Security Notes

- **API Keys**: Never commit API keys to version control
- **Environment Variables**: Preferred for CI/CD environments
- **Config Files**: Keep `.codesolairc` private (chmod 600)
- **Command Line**: Avoid passing API keys via CLI arguments

## 📚 Next Steps

After installation:

1. **Read the README**: Complete feature overview
2. **Try examples**: Test different use cases
3. **Explore options**: `codesolai --help`
4. **Join community**: GitHub discussions and issues

Happy coding with CodeSolAI! 🎉
