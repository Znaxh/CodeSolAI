# Building CodeSolAI: Your Own Autonomous AI Agent CLI Tool

## What is CodeSolAI and Why Should You Care?

Imagine having an AI assistant that doesn't just chat with you, but actually *does* things. CodeSolAI is an autonomous AI agent that can:

- **Read and write files** on your computer
- **Execute system commands** safely
- **Analyze code** and generate documentation
- **Work with multiple AI providers** (Claude, GPT, Gemini)
- **Chain multiple actions** together autonomously

**[GIF NEEDED: Terminal showing CodeSolAI analyzing a codebase, creating documentation, and running tests - all in one command]**

Think of it as having a junior developer who never gets tired, never makes typos, and can work with any programming language.

## Real-World Magic: What Can It Actually Do?

### For Developers
```bash
# Automatically analyze your entire codebase and create docs
codesolai --agent "Analyze all Python files and create comprehensive README"

# Generate test suites for your functions
codesolai --agent "Create unit tests for all functions in src/utils.py"
```

### For DevOps Engineers
```bash
# Audit your configuration files
codesolai --agent "Check all Docker files for security best practices"

# Set up monitoring
codesolai --agent "Create a monitoring setup with Prometheus and Grafana configs"
```

### For Data Analysts
```bash
# Process messy CSV files
codesolai --agent "Clean and analyze all CSV files in data/ directory, generate summary report"
```

**[VIDEO NEEDED: Split screen showing a complex task request on the left and CodeSolAI autonomously executing multiple steps on the right]**

## The 30-Second Demo

Here's what it looks like in action:

```bash
$ codesolai --agent --autonomous "Set up a Flask web app with authentication"

🤖 Planning task execution...
📁 Creating project structure...
📝 Writing Flask application code...
🔐 Implementing user authentication...
🧪 Generating test files...
📋 Creating documentation...
✅ Task completed successfully!
```

**[GIF NEEDED: The above command running in terminal with spinner animations and checkmarks appearing as each step completes]**

## Architecture: How the Magic Works

```
codesolai/
├── cli.py              # Your terminal interface
├── agent.py            # The brain that makes decisions
├── tools/              # The hands that do the work
│   ├── filesystem.py   # Reads/writes files
│   ├── executor.py     # Runs commands
│   └── analyzer.py     # Analyzes code
└── providers/          # Multiple AI backends
    ├── claude.py
    ├── gemini.py
    └── gpt.py
```

Think of it like this:
- **CLI** = Your voice (how you talk to the agent)
- **Agent** = The brain (decides what to do)
- **Tools** = The hands (actually does things)
- **Providers** = The knowledge (different AI models)

## Let's Build It: Step by Step

### Step 1: Project Setup (2 minutes)

First, let's create our project structure:

```bash
# Create and enter project directory
mkdir codesolai && cd codesolai

# Initialize with modern Python tooling
uv init
uv add click rich anthropic google-generativeai openai aiohttp aiofiles
```

**[GIF NEEDED: Terminal showing the project creation and dependency installation process]**

### Step 2: The CLI Interface (5 minutes)

Create the main entry point that users will interact with:

```python
# cli.py
import click
from rich.console import Console

console = Console()

@click.command()
@click.argument('prompt', nargs=-1)
@click.option('--agent/--no-agent', default=False)
@click.option('--autonomous', is_flag=True)
@click.option('--provider', '-p', help='AI provider to use')
def main(prompt, agent, autonomous, provider):
    """CodeSolAI - Your autonomous AI assistant"""
    
    if not prompt:
        console.print("❌ Please provide a task!")
        return
    
    task = ' '.join(prompt)
    
    if agent:
        # Agent mode - can use tools
        run_agent_mode(task, autonomous, provider)
    else:
        # Simple chat mode
        run_simple_mode(task, provider)
```

This gives us a clean interface where users can choose between:
- **Simple mode**: Just chat with AI
- **Agent mode**: AI can use tools
- **Autonomous mode**: AI works without asking permission

### Step 3: Building the Brain (10 minutes)

The agent is the decision-making component:

```python
# agent.py
import re
import json
from typing import List, Dict

class Agent:
    def __init__(self, provider, autonomous=False):
        self.provider = provider
        self.autonomous = autonomous
        self.tools = self._load_tools()
    
    async def process_task(self, task: str) -> str:
        # Step 1: Ask AI what to do
        plan = await self._create_plan(task)
        
        # Step 2: Parse the AI's response for actions
        actions = self._extract_actions(plan)
        
        # Step 3: Execute each action
        results = []
        for action in actions:
            if not self.autonomous:
                if not self._confirm_action(action):
                    continue
            
            result = await self._execute_action(action)
            results.append(result)
        
        # Step 4: Return summary
        return self._format_results(results)
    
    def _extract_actions(self, response: str) -> List[Dict]:
        """Parse AI response for ACTION/PARAMETERS patterns"""
        actions = []
        pattern = r'ACTION:\s*(\w+)\s*\nPARAMETERS:\s*(\{.*?\})'
        
        for match in re.finditer(pattern, response, re.DOTALL):
            tool_name = match.group(1)
            try:
                params = json.loads(match.group(2))
                actions.append({'tool': tool_name, 'params': params})
            except json.JSONDecodeError:
                continue
        
        return actions
```

**The key insight**: We teach the AI to format its responses in a structured way that we can parse and execute.

### Step 4: Creating the Tools (15 minutes)

Tools are what give the agent its superpowers. Let's start with the filesystem tool:

```python
# tools/filesystem.py
import aiofiles
import os
from pathlib import Path

class FilesystemTool:
    name = "filesystem"
    
    async def execute(self, params):
        operation = params.get('operation')
        path = params.get('path', '.')
        
        # Security first!
        if not self._is_safe_path(path):
            return {"error": "Access denied to that path"}
        
        if operation == 'read':
            return await self._read_file(path)
        elif operation == 'write':
            content = params.get('content', '')
            return await self._write_file(path, content)
        elif operation == 'list':
            return await self._list_directory(path)
    
    async def _read_file(self, path: str):
        try:
            async with aiofiles.open(path, 'r') as f:
                content = await f.read()
            return {"success": True, "content": content}
        except FileNotFoundError:
            return {"error": f"File not found: {path}"}
    
    def _is_safe_path(self, path: str) -> bool:
        """Prevent access to system files"""
        abs_path = os.path.abspath(path)
        current_dir = os.path.abspath('.')
        return abs_path.startswith(current_dir)
```

**[VIDEO NEEDED: Demonstration of the filesystem tool reading a file, writing content, and the security restrictions preventing access to /etc/passwd]**

And here's the command execution tool:

```python
# tools/executor.py
import asyncio
import subprocess

class ExecutorTool:
    name = "executor"
    
    # Security: Block dangerous commands
    BLOCKED_COMMANDS = [
        'rm -rf', 'sudo', 'format', 'fdisk', 
        'shutdown', 'reboot', 'passwd'
    ]
    
    async def execute(self, params):
        command = params.get('command', '')
        
        if self._is_dangerous(command):
            return {"error": "Command blocked for security"}
        
        try:
            # Run with timeout to prevent hanging
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                timeout=30
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "success": process.returncode == 0,
                "stdout": stdout.decode(),
                "stderr": stderr.decode()
            }
        except asyncio.TimeoutError:
            return {"error": "Command timed out"}
    
    def _is_dangerous(self, command: str) -> bool:
        return any(blocked in command.lower() 
                  for blocked in self.BLOCKED_COMMANDS)
```

**Security is crucial**: We block dangerous commands and restrict file access to prevent the AI from doing anything harmful.

### Step 5: Multiple AI Providers (8 minutes)

Supporting multiple AI providers gives users choice and redundancy:

```python
# providers/base.py
from abc import ABC, abstractmethod

class BaseProvider(ABC):
    @abstractmethod
    async def call(self, prompt: str) -> str:
        pass

# providers/claude.py
import anthropic

class ClaudeProvider(BaseProvider):
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    async def call(self, prompt: str) -> str:
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

# Similar classes for Gemini and GPT...
```

The provider manager handles switching between them:

```python
# providers/manager.py
class ProviderManager:
    def __init__(self, config):
        self.providers = {
            'claude': ClaudeProvider(config.claude_key),
            'gemini': GeminiProvider(config.gemini_key),
            'gpt': GPTProvider(config.openai_key)
        }
    
    async def call(self, provider_name: str, prompt: str) -> str:
        if provider_name not in self.providers:
            provider_name = 'gemini'  # Default fallback
        
        return await self.providers[provider_name].call(prompt)
```

**[GIF NEEDED: Terminal showing user switching between providers with --provider claude, --provider gemini, etc.]**

### Step 6: The Enhanced Prompt (5 minutes)

This is where the magic happens. We teach the AI how to use our tools:

```python
def create_enhanced_prompt(self, user_task: str) -> str:
    return f"""You are an autonomous AI agent with access to tools.

Available tools:
- filesystem: Read/write files, list directories
  Format: ACTION: filesystem
         PARAMETERS: {{"operation": "read|write|list", "path": "file.txt", "content": "text"}}

- executor: Run system commands safely
  Format: ACTION: executor
         PARAMETERS: {{"command": "ls -la"}}

When you need to use tools, format your response exactly like this:

ACTION: tool_name
PARAMETERS: {{"param1": "value1", "param2": "value2"}}

You can use multiple actions in sequence.

User task: {user_task}

Think step by step:
1. What needs to be done?
2. What tools do I need?
3. In what order?

Then provide your response with the necessary actions."""
```

This prompt template teaches the AI:
1. What tools are available
2. How to format tool calls
3. To think step by step
4. To use multiple tools in sequence

### Step 7: Putting It All Together (5 minutes)

Now we connect all the pieces:

```python
# main.py
async def run_agent_mode(task: str, autonomous: bool, provider: str):
    console.print(f"🤖 Processing task: {task}")
    
    # Initialize components
    agent = Agent(provider, autonomous)
    
    # Process the task
    with console.status("[bold green]Thinking..."):
        result = await agent.process_task(task)
    
    # Display results
    console.print(f"\n✅ {result}")

# Entry point
if __name__ == "__main__":
    main()
```

**[VIDEO NEEDED: Complete workflow showing a user giving a complex task and the agent breaking it down into steps, executing each one, and providing a final summary]**

## Testing: Making Sure It Works

Good testing is essential for an autonomous system:

```python
# tests/test_agent.py
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_action_parsing():
    agent = Agent("test_provider")
    
    response = """I'll help you with that.
    
    ACTION: filesystem
    PARAMETERS: {"operation": "read", "path": "test.py"}
    
    ACTION: executor
    PARAMETERS: {"command": "python test.py"}
    """
    
    actions = agent._extract_actions(response)
    
    assert len(actions) == 2
    assert actions[0]['tool'] == 'filesystem'
    assert actions[1]['tool'] == 'executor'
```

Run tests with: `pytest tests/ -v`

**[GIF NEEDED: Terminal showing test suite running with all tests passing]**

## Configuration: Making It User-Friendly

Create a setup wizard for first-time users:

```python
# setup.py
from rich.prompt import Prompt
import json

def setup_wizard():
    console.print("🚀 Welcome to CodeSolAI Setup!")
    
    config = {}
    
    # Get AI provider preferences
    config['default_provider'] = Prompt.ask(
        "Choose your default AI provider",
        choices=['claude', 'gemini', 'gpt'],
        default='gemini'
    )
    
    # Get API keys
    if Prompt.ask("Do you have an Anthropic Claude API key?", 
                  choices=['y', 'n']) == 'y':
        config['claude_key'] = Prompt.ask("Enter Claude API key", password=True)
    
    # Save configuration
    with open(Path.home() / '.codesolairc', 'w') as f:
        json.dump(config, f, indent=2)
    
    console.print("✅ Setup complete!")
```

**[GIF NEEDED: Setup wizard running interactively, asking for preferences and API keys]**

## Advanced Features

### Interactive Mode
```bash
$ codesolai --interactive
CodeSolAI Interactive Mode - Type '/help' for commands

You: Create a Python script that processes CSV files
AI: I'll create a CSV processing script for you.

ACTION: filesystem
PARAMETERS: {"operation": "write", "path": "csv_processor.py", "content": "import pandas as pd..."}

✅ Created csv_processor.py

You: Now test it with sample data
AI: I'll create some sample data and test the script...
```

### Chain of Thought Reasoning
The agent can explain its thinking:

```bash
$ codesolai --agent --verbose "Set up a web scraper"

🤖 Task: Set up a web scraper
🧠 Thinking:
   1. Need to create Python script with requests/beautifulsoup
   2. Should include error handling and rate limiting
   3. Add example usage and documentation

📝 Step 1: Creating main scraper script...
📝 Step 2: Adding configuration file...
📝 Step 3: Creating example usage...
✅ Web scraper setup complete!
```

## Real-World Usage Examples

### Code Analysis Workflow
```bash
# Analyze code quality across entire project
codesolai --agent "Analyze all Python files for code quality issues, create a report with suggestions"

# Result: Gets code quality report with specific recommendations
```

### Documentation Generation
```bash
# Generate comprehensive documentation
codesolai --agent "Create API documentation for all functions in src/, include examples"

# Result: Auto-generated docs with code examples
```

### Test Suite Creation
```bash
# Create comprehensive test coverage
codesolai --agent "Generate unit tests for all classes in models/, aim for 90% coverage"

# Result: Complete test suite with high coverage
```

**[VIDEO NEEDED: Real-world scenario showing a developer asking CodeSolAI to refactor legacy code, with the agent analyzing files, suggesting improvements, and implementing changes]**

## Security: Keeping Things Safe

Security features built into CodeSolAI:

1. **Path Validation**: Can't access files outside project directory
2. **Command Filtering**: Blocks dangerous system commands
3. **Confirmation Mode**: Asks permission before executing actions
4. **Audit Logging**: Records all actions taken
5. **Sandboxing**: Optional isolation mode for untrusted tasks

```python
# Example: Safe file access
def validate_path(path: str) -> bool:
    abs_path = os.path.abspath(path)
    current_dir = os.path.abspath('.')
    return abs_path.startswith(current_dir)  # Must be in current directory

# Example: Command filtering
BLOCKED_COMMANDS = [
    'rm -rf', 'sudo', 'format', 'shutdown', 
    'reboot', 'passwd', 'chmod 777'
]
```

## Installation and Distribution

### Package It Up
```toml
# pyproject.toml
[project]
name = "codesolai"
version = "1.0.0"
description = "Autonomous AI Agent CLI Tool"
dependencies = [
    "click>=8.0.0",
    "rich>=13.0.0",
    "anthropic>=0.25.0",
    "aiofiles>=23.0.0"
]

[project.scripts]
codesolai = "codesolai.cli:main"
```

### Install Options
```bash
# From PyPI (when published)
pip install codesolai

# From source
git clone https://github.com/znaxh/codesolai.git
cd codesolai
pip install -e .

# Development mode
pip install -e ".[dev]"
```

## Performance Tips

- **Concurrent Execution**: Run up to 3 tools simultaneously
- **Smart Caching**: Cache AI responses for repeated patterns
- **Streaming Output**: Show progress as tasks execute
- **Resource Management**: Automatic cleanup and timeout handling

```python
# Example: Concurrent tool execution
async def execute_tools_concurrently(self, actions):
    semaphore = asyncio.Semaphore(3)  # Max 3 concurrent
    
    async def execute_with_limit(action):
        async with semaphore:
            return await self.execute_tool(action)
    
    tasks = [execute_with_limit(action) for action in actions]
    return await asyncio.gather(*tasks)
```

## Troubleshooting Common Issues

### Issue 1: API Key Not Working
```bash
# Check configuration
codesolai --setup

# Test connection
codesolai --test-connection claude
```

### Issue 2: Tool Execution Fails
```bash
# Run in verbose mode to see details
codesolai --agent --verbose "your task here"

# Check permissions
ls -la ~/.codesolairc
```

### Issue 3: Slow Performance
```bash
# Use faster provider
codesolai --provider gemini "your task"

# Enable concurrent execution
codesolai --agent --concurrent "your task"
```

## What You've Built

Congratulations! You now have:

✅ **A complete autonomous AI agent** that can execute complex tasks  
✅ **Multi-provider AI support** (Claude, GPT, Gemini)  
✅ **Secure tool system** with built-in safety controls  
✅ **Professional CLI interface** with rich output formatting  
✅ **Comprehensive test suite** ensuring reliability  
✅ **Easy deployment** with proper packaging  

## Next Steps: Making It Even Better

### Potential Enhancements
1. **Plugin System**: Let others create custom tools
2. **Web Interface**: Browser-based UI for non-technical users
3. **Team Collaboration**: Multi-user support with shared configs
4. **Advanced Planning**: More sophisticated task decomposition
5. **Integration APIs**: REST API for other applications

### Community Features
1. **Tool Marketplace**: Share custom tools with others
2. **Task Templates**: Pre-built workflows for common tasks
3. **Learning Mode**: Agent learns from user feedback
4. **Collaborative Agents**: Multiple agents working together

## The Big Picture

You've built more than just a CLI tool—you've created a foundation for autonomous AI systems. This architecture can be adapted for:

- **DevOps Automation**: Infrastructure management and monitoring
- **Content Creation**: Automated writing and media generation  
- **Data Processing**: Large-scale analysis and transformation
- **Quality Assurance**: Automated testing and validation
- **Research Assistance**: Information gathering and analysis

**[VIDEO NEEDED: Montage showing different use cases - DevOps automation, content creation, data processing, etc.]**

## Key Takeaways

1. **Start Simple**: Basic chat interface → Add tools → Make autonomous
2. **Security First**: Always validate inputs and restrict dangerous operations
3. **User Experience Matters**: Rich terminal interfaces make complex tools approachable
4. **Test Everything**: Autonomous systems need comprehensive testing
5. **Make It Extensible**: Modular architecture allows easy feature additions

The future belongs to AI agents that don't just talk, but act. You've just built one of them.

**[GIF NEEDED: Final celebration showing CodeSolAI successfully completing a complex multi-step task with confetti animation]**

---

*Ready to build your own autonomous AI agent? The complete source code and additional examples are available on GitHub. Star the repo if this helped you build something awesome!*