# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-27

### Added
- **Complete Python Conversion**: Converted from Node.js visaire-cli to Python-based CodeSolAI
- **Modern CLI Interface**: Built with Click framework for robust command-line interaction
- **Multi-Provider Support**: Support for Claude (Anthropic), GPT (OpenAI), and Gemini (Google)
- **Interactive Setup Wizard**: Easy first-time configuration with `codesolai --setup`
- **Interactive Chat Mode**: Persistent conversation sessions with `codesolai --interactive`
- **Rich Terminal Output**: Beautiful formatting with Rich library
- **Configuration Management**: JSON-based configuration with `.codesolairc` files
- **API Key Management**: Secure storage and validation of API keys
- **Async HTTP Client**: Modern async implementation with httpx
- **Error Handling**: Comprehensive error handling with retry logic
- **Spinner Animations**: Dynamic loading indicators with elapsed time
- **Python Package**: Proper Python packaging with pyproject.toml

### Features
- **Provider Management**: Easy switching between AI providers
- **Model Selection**: Support for different models per provider
- **Configuration Options**: Timeout, retries, temperature, max tokens
- **Piped Input**: Support for stdin input (`echo "prompt" | codesolai`)
- **Command-line Options**: Full CLI with help, version, config commands
- **Virtual Environment**: Modern Python packaging with uv support

### Technical Details
- **Python 3.9+**: Modern Python with type hints and async/await
- **Dependencies**: Click, httpx, Rich, Pydantic, PyYAML, aiofiles
- **Architecture**: Modular design with provider plugins
- **Testing**: Ready for comprehensive test suite
- **Documentation**: Complete README and inline documentation

### Migration from visaire-cli
- **API Compatibility**: Same command-line interface and options
- **Configuration**: Automatic migration from `.visairerc` to `.codesolairc`
- **Feature Parity**: All core functionality preserved
- **Enhanced UX**: Improved error messages and user feedback

### Future Roadmap
- **Agent System**: Autonomous task execution capabilities
- **Tool System**: File operations and command execution
- **Plugin Architecture**: Extensible tool and provider system
- **Test Suite**: Comprehensive testing framework
- **Advanced Features**: Streaming responses, function calling

## [Previous Versions]
Previous versions were Node.js-based visaire-cli. This is the first Python release.
