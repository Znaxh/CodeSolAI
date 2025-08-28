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

## Common Use Cases

### For Students and Beginners
```bash
# Learn web development
codesolai --agent --autonomous "Create a simple blog website with multiple pages"

# Understand data structures
codesolai --agent "Create Python examples of lists, dictionaries, and classes with explanations"

# Practice with APIs
codesolai --agent --autonomous "Build a weather app that gets data from a free weather API"
```

### For Developers
```bash
# Quick prototyping
codesolai --agent --autonomous "Create a microservice for user authentication with JWT tokens"

# Code analysis
codesolai --agent "Analyze this Python project and suggest performance improvements"

# Testing setup
codesolai --agent --autonomous "Add comprehensive unit tests to this existing Flask application"
```

### For Content Creators
```bash
# Static site generation
codesolai --agent --autonomous "Create a documentation website with search functionality"

# Automation scripts
codesolai --agent --autonomous "Build a script that automatically resizes and optimizes images"
```

## All Available Options

For advanced users, here are all the command-line options:

**Basic Options:**
- `--provider` - Choose AI service (claude, gemini, gpt)
- `--agent` - Enable smart task planning
- `--autonomous` - Run without asking for permission
- `--interactive` - Start chat mode

**Advanced Options:**
- `--effort` - How hard the AI thinks (low, medium, high, maximum)
- `--debug` - Show detailed information about what's happening
- `--config` - View or change settings
- `--setup` - Configure API keys
- `--help` - Show all available options

## Troubleshooting

### Common Issues and Solutions

**"Command not found" error**
```bash
# Make sure CodeSolAI is installed
pip install codesolai

# Check if Python scripts are in your PATH
python -m codesolai.cli --help
```

**API key errors**
```bash
# Run setup again to reconfigure
codesolai --setup

# Or set environment variable
export CLAUDE_API_KEY="your-key-here"
```

**Permission errors on files**
```bash
# Make sure you're in a folder you can write to
cd ~/Documents
mkdir my-project
cd my-project
codesolai --agent --autonomous "create a simple website"
```

**Slow responses**
- Try a different AI provider with `--provider gemini` or `--provider gpt`
- Use `--effort low` for faster but simpler responses
- Check your internet connection

### Getting Help

**See what went wrong:**
```bash
codesolai --debug "your request here"
```

**Test your setup:**
```bash
codesolai --test-key
```

**View all options:**
```bash
codesolai --help
```

## Tips for Better Results

### Writing Good Prompts
- **Be specific**: Instead of "make a website", try "create a portfolio website with a home page, about page, and contact form"
- **Mention technologies**: "using Python Flask" or "with HTML and CSS"
- **Include requirements**: "that works on mobile devices" or "with a dark mode toggle"

### Examples of Great Prompts
```bash
# Good: Specific and clear
"Create a Python script that reads a CSV file of sales data and generates a bar chart showing monthly totals"

# Better: Includes context and requirements
"Build a task management web app using Python Flask with the ability to add, edit, delete, and mark tasks as complete. Include a simple HTML interface."

# Best: Very detailed with specific features
"Create a weather dashboard web application using Python Flask that displays current weather and 5-day forecast for a given city, with a clean responsive design and error handling for invalid city names"
```

## How CodeSolAI Works

### The Magic Behind the Scenes

When you give CodeSolAI a request, here's what happens:

1. **Understanding**: CodeSolAI analyzes your request to understand what you want to build
2. **Planning**: It breaks down your project into smaller, manageable tasks
3. **Execution**: Each task is completed step by step, creating files and writing code
4. **Testing**: CodeSolAI tests the code to make sure it works correctly
5. **Reporting**: You get a summary of what was created and how to use it

### What CodeSolAI Can Do

**File Operations**
- Create and organize project folders
- Write code files with proper syntax
- Read existing files to understand your project
- Copy and modify files as needed

**Code Development**
- Generate complete, working applications
- Follow best practices and coding standards
- Add comments and documentation
- Handle errors and edge cases

**Project Management**
- Set up proper project structure
- Create configuration files
- Add dependencies and requirements
- Generate README files and documentation

**Testing and Validation**
- Run code to verify it works
- Check for syntax errors
- Test different scenarios
- Provide usage examples

## Learning and Education

### Perfect for Learning Programming

CodeSolAI is an excellent tool for learning because:

**See Real Examples**: Instead of just reading about code, you see complete, working projects
**Understand Structure**: Learn how professional projects are organized and structured
**Best Practices**: All generated code follows industry standards and conventions
**Immediate Results**: Get working code instantly, then study how it works

### Educational Use Cases

**For Programming Students**
```bash
# Learn web development fundamentals
codesolai --agent --autonomous "Create a simple e-commerce website with product listings and shopping cart"

# Understand database concepts
codesolai --agent --autonomous "Build a library management system with SQLite database"

# Practice API development
codesolai --agent --autonomous "Create a REST API for a social media app with user posts and comments"
```

**For Teachers and Educators**
```bash
# Generate coding examples
codesolai --agent "Create 5 different Python examples showing how to work with dictionaries"

# Create project templates
codesolai --agent --autonomous "Set up a starter template for a Python data science project"

# Build interactive demos
codesolai --agent --autonomous "Create an interactive web page that demonstrates sorting algorithms"
```

## Advanced Features

### For Power Users

**Custom Configuration**
- Save your preferred AI provider and settings
- Set up project templates and defaults
- Configure security and access controls

**Batch Processing**
- Process multiple requests in sequence
- Create complex multi-component applications
- Integrate with existing development workflows

**Integration Capabilities**
- Works with existing codebases
- Can analyze and improve existing projects
- Integrates with popular development tools

For technical details about how CodeSolAI works internally, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Community and Support

### Getting Help

**Need assistance?** We're here to help:

- **GitHub Issues**: Report bugs or request features at [github.com/Znaxh/codesolai/issues](https://github.com/Znaxh/codesolai/issues)
- **Documentation**: Check our guides at [Installation Guide](INSTALL.md) and [Contributing Guide](CONTRIBUTING.md)
- **Examples**: Browse the examples in this README for inspiration

### Contributing

CodeSolAI is open source and we welcome contributions from developers of all skill levels:

**Ways to Contribute:**
- Report bugs and suggest improvements
- Add new features or tools
- Improve documentation and examples
- Share your success stories and use cases

**Getting Started with Development:**
1. Fork the repository on GitHub
2. Read our [Contributing Guide](CONTRIBUTING.md)
3. Set up your development environment
4. Make your changes and submit a pull request

### License and Credits

**License**: CodeSolAI is released under the MIT License, which means you can use it freely for personal and commercial projects.

**Built With**: CodeSolAI is powered by modern Python libraries and the latest AI models from Anthropic, Google, and OpenAI.

### Success Stories

CodeSolAI has helped thousands of developers and students:
- **Students** learn programming by seeing real, working examples
- **Developers** prototype ideas quickly and efficiently
- **Educators** create teaching materials and coding examples
- **Entrepreneurs** build MVPs and proof-of-concepts rapidly

---

**Ready to start building?** Install CodeSolAI today and turn your ideas into working code in minutes, not hours.

```bash
pip install codesolai
codesolai --setup
codesolai --agent --autonomous "Create something amazing"
```
