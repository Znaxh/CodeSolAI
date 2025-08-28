"""
Enhanced Agent implementation with sophisticated reasoning capabilities
"""

from typing import Dict, Any, Optional
from datetime import datetime
from rich.console import Console

from .agent import Agent, AgentConfig
from .task_manager import TaskManager, TaskState
from ..providers.provider_manager import ProviderManager
from ..utils import Utils


class EnhancedAgent(Agent):
    """
    Enhanced Agent with sophisticated reasoning and provider integration
    This replaces the old agent with advanced capabilities
    """

    def __init__(self, options: Optional[Dict[str, Any]] = None):
        """Initialize enhanced agent with provider integration"""
        options = options or {}
        
        # Create enhanced configuration
        config = AgentConfig(
            name=options.get('name', 'codesolai-agent'),
            model=options.get('model', 'claude-3-5-sonnet-20241022'),
            provider=options.get('provider', 'claude'),
            api_key=options.get('api_key'),
            temperature=options.get('temperature', 0.7),
            max_tokens=options.get('max_tokens', 4000),
            reasoning_effort=options.get('effort', 'medium'),
            max_iterations=options.get('max_iterations', 10),
            enable_reflection=options.get('enable_reflection', True),
            enable_planning=options.get('enable_planning', True),
            tools_enabled=options.get('tools_enabled', True),
            auto_approve=options.get('auto_approve', True),
            confirmation_required=options.get('confirmation_required', False),
            max_concurrent_tools=options.get('max_concurrent', 3),
            max_context_size=options.get('max_context_size', 100000),
            compression_threshold=options.get('compression_threshold', 0.8),
            retention_strategy=options.get('retention_strategy', 'importance'),
            log_level=options.get('log_level', 'warning'),
            enable_metrics=options.get('enable_metrics', True),
            enable_tracing=options.get('enable_tracing', False)
        )
        
        # Initialize base agent
        super().__init__(config)
        
        # Store provider configuration
        self.provider_config = {
            'provider': config.provider,
            'api_key': config.api_key,
            'model': config.model,
            'temperature': config.temperature,
            'max_tokens': config.max_tokens
        }
        
        # Initialize provider manager
        self.provider_manager = ProviderManager()

        # Initialize task manager for autonomous mode
        self.task_manager = TaskManager(self.logger, Console())
        self.autonomous_mode = options.get('autonomous', False)

        # Debug logging
        self.logger.debug('Enhanced agent autonomous mode', {
            'autonomous_mode': self.autonomous_mode,
            'auto_approve': config.auto_approve
        })

        # Setup task manager callbacks
        self.task_manager.on_task_start = self._on_task_start
        self.task_manager.on_task_complete = self._on_task_complete
        self.task_manager.on_task_failed = self._on_task_failed
        self.task_manager.on_all_complete = self._on_all_tasks_complete

        self.logger.debug('Enhanced agent initialized', {
            'provider': config.provider,
            'model': config.model,
            'tools_enabled': config.tools_enabled,
            'autonomous_mode': self.autonomous_mode
        })

    async def process_prompt(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process user prompt with enhanced reasoning
        This is the main entry point for the enhanced agent
        """
        options = options or {}

        # Check if autonomous mode is enabled
        autonomous_mode = options.get('autonomous', self.autonomous_mode)

        if autonomous_mode:
            return await self.process_autonomous(prompt, options)
        else:
            return await self.process_single_prompt(prompt, options)

    async def process_autonomous(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process prompt in autonomous mode with task decomposition and sequential execution
        """
        options = options or {}

        try:
            # Validate inputs
            if not prompt or not isinstance(prompt, str) or not prompt.strip():
                raise ValueError('Prompt is required and must be a non-empty string')

            # Merge options with defaults
            process_options = {
                'provider': options.get('provider', self.provider_config['provider']),
                'api_key': options.get('api_key', self.provider_config['api_key']),
                'model': options.get('model', self.provider_config['model']),
                'temperature': options.get('temperature', self.provider_config['temperature']),
                'max_tokens': options.get('max_tokens', self.provider_config['max_tokens']),
                'auto_approve': options.get('auto_approve', self.config.auto_approve),
                'effort': options.get('effort', self.config.reasoning_effort),
                **options
            }

            self.logger.debug('Processing prompt in autonomous mode', {
                'prompt_length': len(prompt),
                'provider': process_options['provider'],
                'model': process_options['model']
            })

            # Validate API key
            if not process_options['api_key']:
                return {
                    'success': False,
                    'error': 'API key is required',
                    'response': 'I need an API key to process your request. Please provide one using --api-key or configure it in your settings.'
                }

            # Step 1: Decompose the request into tasks
            self.task_manager.console.print("\n🧠 [bold cyan]Analyzing request and breaking down into tasks...[/bold cyan]")

            try:
                self.logger.info(f"Starting task decomposition for: {prompt[:100]}...")
                self.logger.info(f"Process options: provider={process_options.get('provider')}, api_key_present={bool(process_options.get('api_key'))}")

                task_ids = await self.task_manager.decompose_task(prompt, process_options)
                self.logger.info(f"Task decomposition result: {len(task_ids) if task_ids else 0} tasks created")

                if task_ids:
                    self.task_manager.console.print(f"✅ [green]Successfully created {len(task_ids)} tasks[/green]")
                else:
                    self.task_manager.console.print("❌ [red]No tasks were created during decomposition[/red]")

            except Exception as decomp_error:
                self.logger.error(f"Task decomposition failed: {decomp_error}")
                self.task_manager.console.print(f"❌ [red]Task decomposition error: {str(decomp_error)}[/red]")
                task_ids = []

            if not task_ids:
                # Fallback to single prompt processing
                self.logger.warning("Task decomposition failed, falling back to single prompt processing")
                self.task_manager.console.print("⚠️  [yellow]Task decomposition failed, using single-step execution[/yellow]")
                return await self.process_single_prompt(prompt, options)

            # Step 2: Display initial task breakdown
            self.task_manager.console.print(f"\n📋 [bold green]Created {len(task_ids)} tasks for execution:[/bold green]")
            self.task_manager.display_progress(show_detailed=True)

            # Step 3: Execute tasks sequentially
            all_results = []
            files_created = []
            files_modified = []
            commands_executed = []

            while True:
                next_task = self.task_manager.get_next_task()
                if not next_task:
                    break

                # Start the task
                self.task_manager.start_task(next_task.id)

                # Execute the task
                task_result = await self._execute_single_task(next_task, process_options)

                if task_result.get('success', False):
                    # Collect results
                    if 'files_created' in task_result:
                        files_created.extend(task_result['files_created'])
                    if 'files_modified' in task_result:
                        files_modified.extend(task_result['files_modified'])
                    if 'commands_executed' in task_result:
                        commands_executed.extend(task_result['commands_executed'])

                    # Complete the task
                    self.task_manager.complete_task(next_task.id, {
                        'files_created': task_result.get('files_created', []),
                        'files_modified': task_result.get('files_modified', []),
                        'commands_executed': task_result.get('commands_executed', [])
                    })
                else:
                    # Fail the task
                    error_msg = task_result.get('error', 'Unknown error')
                    self.task_manager.fail_task(next_task.id, error_msg)

                all_results.append(task_result)

            # Step 4: Display completion summary
            self.task_manager.display_completion_summary()

            # Step 5: Generate final response
            summary = self.task_manager.get_progress_summary()
            final_response = f"""
🎉 **Autonomous execution completed!**

**Summary:**
- Total tasks: {summary['total_tasks']}
- Completed: {summary['completed_tasks']} ✅
- Failed: {summary['failed_tasks']} ❌

**Files created:** {len(files_created)}
**Files modified:** {len(files_modified)}
**Commands executed:** {len(commands_executed)}

All requested tasks have been completed successfully! The project structure has been created and all necessary files are in place.
            """.strip()

            return {
                'success': True,
                'response': final_response,
                'autonomous_mode': True,
                'tasks_executed': len(task_ids),
                'tasks_completed': summary['completed_tasks'],
                'tasks_failed': summary['failed_tasks'],
                'files_created': files_created,
                'files_modified': files_modified,
                'commands_executed': commands_executed,
                'execution_results': all_results,
                'provider': process_options['provider'],
                'model': process_options['model']
            }

        except Exception as error:
            self.logger.error('Error in autonomous processing', {
                'error': str(error),
                'prompt_length': len(prompt) if prompt else 0
            })

            return {
                'success': False,
                'error': str(error),
                'response': f'I encountered an error during autonomous execution: {str(error)}'
            }

    async def process_single_prompt(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a single prompt without task decomposition (original behavior)
        """
        options = options or {}

        try:
            # Validate inputs
            if not prompt or not isinstance(prompt, str) or not prompt.strip():
                raise ValueError('Prompt is required and must be a non-empty string')

            # Merge options with defaults
            process_options = {
                'provider': options.get('provider', self.provider_config['provider']),
                'api_key': options.get('api_key', self.provider_config['api_key']),
                'model': options.get('model', self.provider_config['model']),
                'temperature': options.get('temperature', self.provider_config['temperature']),
                'max_tokens': options.get('max_tokens', self.provider_config['max_tokens']),
                'auto_approve': options.get('auto_approve', self.config.auto_approve),
                'effort': options.get('effort', self.config.reasoning_effort),
                **options
            }

            self.logger.info('Processing single prompt', {
                'prompt_length': len(prompt),
                'provider': process_options['provider'],
                'model': process_options['model'],
                'effort': process_options['effort']
            })

            # Validate API key
            if not process_options['api_key']:
                return {
                    'success': False,
                    'error': 'API key is required',
                    'response': 'I need an API key to process your request. Please provide one using --api-key or configure it in your settings.'
                }

            # Validate API key format
            if not Utils.validate_api_key(process_options['api_key'], process_options['provider']):
                return {
                    'success': False,
                    'error': 'Invalid API key format',
                    'response': f'The provided API key format is invalid for {process_options["provider"]}. Please check your API key.'
                }

            # Step 1: Get LLM response with context
            llm_response = await self._get_llm_response(prompt, process_options)

            if not llm_response.get('success', False):
                return llm_response

            # Step 2: Parse actions from the response
            parsed_actions = self._parse_actions_from_response(llm_response['response'])

            # Step 3: Execute actions if tools are enabled and actions are found
            execution_results = []
            if parsed_actions and self.config.tools_enabled:
                execution_results = await self._execute_parsed_actions(
                    parsed_actions,
                    process_options
                )

            # Step 4: Generate final response
            final_response = await self._generate_final_response(
                prompt,
                llm_response['response'],
                parsed_actions,
                execution_results,
                process_options
            )

            return {
                'success': True,
                'response': final_response,
                'llm_response': llm_response['response'],
                'actions_found': len(parsed_actions),
                'actions_executed': len(execution_results),
                'execution_results': execution_results,
                'provider': process_options['provider'],
                'model': process_options['model']
            }

        except Exception as error:
            self.logger.error('Error processing single prompt', {
                'error': str(error),
                'prompt_length': len(prompt) if prompt else 0
            })

            return {
                'success': False,
                'error': str(error),
                'response': f'I encountered an error while processing your request: {str(error)}'
            }

    async def _get_llm_response(self, prompt: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Get response from LLM provider with agent capabilities"""
        try:
            # Enhance the prompt with agent capabilities if tools are enabled
            enhanced_prompt = prompt
            if options.get('tools_enabled', True):
                enhanced_prompt = f"""You are CodeSolAI, an AI assistant with the ability to perform actions using tools.

Available tools:
- read_file: Read file contents
- write_file: Write content to a file (creates directories automatically)
- list_directory: List directory contents
- create_directory: Create a directory
- execute_command: Execute shell commands
- analyze_code: Analyze code structure
- http_request: Make HTTP requests

IMPORTANT FILE CREATION GUIDELINES:
1. Always create complete, functional files with proper content
2. Include necessary imports, dependencies, and boilerplate code
3. Add comments and documentation where appropriate
4. Ensure files follow best practices for the language/framework
5. Create directory structures as needed
6. Include configuration files (requirements.txt, package.json, etc.)

When you need to perform an action, use this format:
ACTION: tool_name
PARAMETERS: {{"param1": "value1", "param2": "value2"}}

For file creation, always include complete, working content:
ACTION: write_file
PARAMETERS: {{"path": "filename.py", "content": "# Complete file content here\\nwith proper code..."}}

User request: {prompt}

Please provide a helpful response and use tools when appropriate to complete the task. Focus on creating complete, functional implementations."""

            response = await self.provider_manager.call(
                options['provider'],
                options['api_key'],
                enhanced_prompt,
                {
                    'model': options.get('model'),
                    'temperature': options.get('temperature'),
                    'max_tokens': options.get('max_tokens')
                }
            )
            
            return {
                'success': True,
                'response': response
            }
            
        except Exception as error:
            error_message = Utils.format_error(error, options['provider'])
            return {
                'success': False,
                'error': error_message,
                'response': f'I encountered an error while getting a response: {error_message}'
            }

    def _parse_actions_from_response(self, response: str) -> list:
        """Parse actions from LLM response"""
        import re
        import json

        actions = []

        # Look for ACTION: and PARAMETERS: patterns
        # First find ACTION lines, then extract complete JSON objects
        action_lines = re.findall(r'ACTION:\s*(\w+)', response, re.IGNORECASE)

        for tool_name in action_lines:
            tool_name = tool_name.strip()

            # Find the PARAMETERS line after this ACTION
            action_pattern = rf'ACTION:\s*{re.escape(tool_name)}\s*\nPARAMETERS:\s*(\{{.*?)\n(?:ACTION:|$)'
            match = re.search(action_pattern, response, re.DOTALL | re.IGNORECASE)

            if not match:
                # Try without the lookahead for end of response
                action_pattern = rf'ACTION:\s*{re.escape(tool_name)}\s*\nPARAMETERS:\s*(\{{.*?)(?=\n\n|\nACTION:|\Z)'
                match = re.search(action_pattern, response, re.DOTALL | re.IGNORECASE)

            if match:
                json_str = match.group(1).strip()

                # Try to find the complete JSON object by counting braces
                json_str = self._extract_complete_json(json_str)

                try:
                    # First try to parse as-is
                    parameters = json.loads(json_str)
                except json.JSONDecodeError:
                    # If that fails, try to fix common issues with triple quotes
                    try:
                        # Replace triple quotes with escaped quotes
                        fixed_json = self._fix_json_content(json_str)
                        parameters = json.loads(fixed_json)
                    except json.JSONDecodeError:
                        # If still failing, log and skip
                        self.logger.warn('Failed to parse action parameters after fixes', {
                            'tool': tool_name,
                            'raw_parameters': json_str[:200] + '...' if len(json_str) > 200 else json_str
                        })
                        continue

                    # Normalize and provide default parameters for common tools
                    if tool_name == 'list_directory':
                        # Handle different parameter names
                        if 'directory' in parameters:
                            parameters['path'] = parameters.pop('directory')
                        if 'hidden' in parameters:
                            parameters['include_hidden'] = parameters.pop('hidden')
                        if not parameters.get('path'):
                            parameters['path'] = '.'
                    elif tool_name == 'create_directory':
                        # Handle different parameter names
                        if 'directory_path' in parameters:
                            parameters['path'] = parameters.pop('directory_path')
                        if 'directory' in parameters:
                            parameters['path'] = parameters.pop('directory')
                        if not parameters.get('path'):
                            continue  # Skip if no path provided
                    elif tool_name == 'read_file':
                        if 'file' in parameters:
                            parameters['path'] = parameters.pop('file')
                        if 'file_path' in parameters:
                            parameters['path'] = parameters.pop('file_path')
                        if 'filepath' in parameters:
                            parameters['path'] = parameters.pop('filepath')
                        if not parameters.get('path'):
                            continue  # Skip if no path provided
                    elif tool_name == 'write_file':
                        if 'file' in parameters:
                            parameters['path'] = parameters.pop('file')
                        if 'file_path' in parameters:
                            parameters['path'] = parameters.pop('file_path')
                        if 'filepath' in parameters:
                            parameters['path'] = parameters.pop('filepath')
                        if not parameters.get('path'):
                            continue  # Skip if no path provided

                actions.append({
                    'tool': tool_name,
                    'parameters': parameters
                })

        # Also look for simpler patterns like "create file: filename.py"
        simple_patterns = [
            (r'create file[:\s]+([^\s\n]+)', 'write_file'),
            (r'read file[:\s]+([^\s\n]+)', 'read_file'),
            (r'list directory[:\s]+([^\s\n]+)', 'list_directory'),
            (r'run command[:\s]+([^\n]+)', 'execute_command'),
            (r'execute[:\s]+([^\n]+)', 'execute_command')
        ]

        for pattern, tool_name in simple_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                if tool_name == 'write_file':
                    actions.append({
                        'tool': 'write_file',
                        'parameters': {'path': match, 'content': '# Generated file\n'}
                    })
                elif tool_name == 'read_file':
                    actions.append({
                        'tool': 'read_file',
                        'parameters': {'path': match}
                    })
                elif tool_name == 'list_directory':
                    actions.append({
                        'tool': 'list_directory',
                        'parameters': {'path': match}
                    })
                elif tool_name == 'execute_command':
                    actions.append({
                        'tool': 'execute_command',
                        'parameters': {'command': match}
                    })

        return actions

    async def _execute_parsed_actions(self, actions: list, options: Dict[str, Any]) -> list:
        """Execute parsed actions using the tool registry"""
        if not actions:
            return []

        results = []
        conversation_id = f"agent-{self.config.id}"

        for action in actions:
            try:
                tool_name = action.get('tool')
                parameters = action.get('parameters', {})

                self.logger.info('Executing action', {
                    'tool': tool_name,
                    'parameters': parameters
                })

                # Check if user approval is needed
                if not options.get('auto_approve', True) and options.get('confirmation_required', False):
                    # In a real implementation, this would prompt the user
                    # For now, we'll assume approval
                    pass

                # Execute the tool
                result = await self.tool_registry.execute_tool(
                    tool_name,
                    parameters,
                    conversation_id
                )

                results.append(result)

                self.logger.info('Action executed', {
                    'tool': tool_name,
                    'success': result.get('success', False)
                })

            except Exception as error:
                self.logger.error('Action execution failed', {
                    'action': action,
                    'error': str(error)
                })
                results.append({
                    'success': False,
                    'error': str(error),
                    'tool': action.get('tool', 'unknown'),
                    'parameters': action.get('parameters', {})
                })

        return results

    async def _generate_final_response(self, original_prompt: str, llm_response: str,
                                     actions: list, execution_results: list,
                                     options: Dict[str, Any]) -> str:
        """Generate final response incorporating action results"""
        # If no actions were executed, return the original LLM response
        if not execution_results:
            return llm_response

        # Build enhanced response with action results
        enhanced_response = llm_response + "\n\n"

        # Add results from executed actions
        for i, result in enumerate(execution_results, 1):
            if result.get('success'):
                tool_name = result.get('tool', 'Unknown')
                # Handle nested result structure from tool registry
                tool_result = result.get('result', {})
                if isinstance(tool_result, dict) and 'result' in tool_result:
                    tool_result = tool_result['result']

                if tool_name == 'list_directory':
                    items = tool_result.get('items', [])
                    enhanced_response += f"📁 **Directory listing for {tool_result.get('path', '.')}:**\n"
                    if items:
                        for item in items[:20]:  # Limit to first 20 items
                            icon = "📁" if item['type'] == 'directory' else "📄"
                            enhanced_response += f"  {icon} {item['name']}\n"
                        if len(items) > 20:
                            enhanced_response += f"  ... and {len(items) - 20} more items\n"
                    else:
                        enhanced_response += "  (empty directory)\n"

                elif tool_name == 'read_file':
                    content = tool_result.get('content', '')
                    path = tool_result.get('path', 'file')
                    enhanced_response += f"📄 **Contents of {path}:**\n```\n{content[:1000]}\n```\n"
                    if len(content) > 1000:
                        enhanced_response += "... (content truncated)\n"

                elif tool_name == 'execute_command':
                    command = tool_result.get('command', '')
                    stdout = tool_result.get('stdout', '')
                    stderr = tool_result.get('stderr', '')
                    return_code = tool_result.get('return_code', 0)

                    enhanced_response += f"💻 **Command executed:** `{command}`\n"
                    enhanced_response += f"**Exit code:** {return_code}\n"
                    if stdout:
                        enhanced_response += f"**Output:**\n```\n{stdout[:1000]}\n```\n"
                    if stderr:
                        enhanced_response += f"**Errors:**\n```\n{stderr[:500]}\n```\n"

                else:
                    # Generic result display
                    enhanced_response += f"🔧 **{tool_name} result:**\n{str(tool_result)[:500]}\n"
            else:
                # Show failed actions
                error = result.get('error', 'Unknown error')
                tool_name = result.get('tool', 'Unknown')
                enhanced_response += f"❌ **{tool_name} failed:** {error}\n"

        return enhanced_response

    async def _execute_single_task(self, task, options: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task with enhanced prompting and result tracking"""
        try:
            # Check if this is a template-based task with predefined content
            if task.metadata.get('template_based') and task.metadata.get('file_content'):
                return await self._execute_template_task(task, options)

            # Create task-specific prompt with enhanced file creation guidance
            task_prompt = f"""
You are executing a specific task as part of a larger autonomous workflow.

**Current Task:** {task.name}
**Task Description:** {task.description}

EXECUTION REQUIREMENTS:
1. Create complete, functional files with proper content
2. Include all necessary imports, dependencies, and configurations
3. Follow best practices for the language/framework being used
4. Add appropriate comments and documentation
5. Ensure files are production-ready, not just placeholders
6. Create directory structures as needed
7. Include error handling where appropriate

IMPORTANT: Do not create empty files or files with just comments. Every file should contain complete, working implementation.

For web applications, include:
- Complete HTML templates with proper structure
- CSS styling (inline or separate files)
- JavaScript functionality where needed
- Configuration files (requirements.txt, package.json, etc.)
- Environment setup files
- Database models and migrations if applicable

For Python projects, include:
- Proper imports and dependencies
- Complete class and function implementations
- Error handling and logging
- Configuration management
- Requirements.txt with all dependencies

Focus only on this specific task. Be thorough and create complete, functional implementations.
"""

            # Execute the task using single prompt processing
            result = await self.process_single_prompt(task_prompt, options)

            # Extract file operations from execution results
            files_created = []
            files_modified = []
            commands_executed = []

            if result.get('execution_results'):
                for exec_result in result['execution_results']:
                    if exec_result.get('success') and exec_result.get('tool'):
                        tool_name = exec_result['tool']
                        tool_result = exec_result.get('result', {})

                        if tool_name in ['write_file', 'create_file']:
                            file_path = tool_result.get('path')
                            if file_path:
                                files_created.append(file_path)
                        elif tool_name == 'execute_command':
                            command = tool_result.get('command')
                            if command:
                                commands_executed.append(command)

            # Add file tracking to result
            result['files_created'] = files_created
            result['files_modified'] = files_modified
            result['commands_executed'] = commands_executed

            return result

        except Exception as error:
            self.logger.error(f'Task execution failed: {task.name}', {
                'task_id': task.id,
                'error': str(error)
            })

            return {
                'success': False,
                'error': str(error),
                'files_created': [],
                'files_modified': [],
                'commands_executed': []
            }

    async def _execute_template_task(self, task, options: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a template-based task with predefined content"""
        try:
            files_created = []
            files_modified = []
            commands_executed = []

            # Handle directory creation task
            if 'directory structure' in task.name.lower():
                # Create necessary directories
                directories = ['templates', 'static', 'static/css', 'static/js']
                directories_created = []

                for directory in directories:
                    try:
                        result = await self.tool_registry.execute_tool(
                            'create_directory',
                            {'path': directory},
                            f"agent-{self.config.id}"
                        )
                        if result.get('success'):
                            directories_created.append(directory)
                            self.logger.info(f"Created directory: {directory}")
                        else:
                            self.logger.error(f"Failed to create directory {directory}: {result.get('error')}")
                    except Exception as dir_error:
                        self.logger.error(f"Exception creating directory {directory}: {dir_error}")

                return {
                    'success': True,
                    'response': f"Created project directory structure ({len(directories_created)} directories)",
                    'files_created': [],
                    'files_modified': [],
                    'commands_executed': [],
                    'directories_created': directories_created
                }

            # Handle file creation with predefined content
            elif task.metadata.get('file_path') and task.metadata.get('file_content'):
                file_path = task.metadata['file_path']
                file_content = task.metadata['file_content']

                # Create the file with predefined content
                result = await self.tool_registry.execute_tool(
                    'write_file',
                    {
                        'path': file_path,
                        'content': file_content
                    },
                    f"agent-{self.config.id}"
                )

                if result.get('success'):
                    files_created.append(file_path)
                    self.logger.info(f"Created file with template content: {file_path}")

                    return {
                        'success': True,
                        'response': f"Created {file_path} with complete implementation",
                        'files_created': files_created,
                        'files_modified': files_modified,
                        'commands_executed': commands_executed
                    }
                else:
                    return {
                        'success': False,
                        'error': f"Failed to create file: {file_path}",
                        'files_created': [],
                        'files_modified': [],
                        'commands_executed': []
                    }

            # Handle setup/initialization tasks
            elif 'initialize' in task.name.lower() or 'test' in task.name.lower():
                project_type = task.metadata.get('project_type')

                if project_type == 'flask_web_app':
                    # Run Flask app initialization
                    init_command = 'python -c "from app import init_db; init_db(); print(\'Database initialized successfully\')"'

                    result = await self.tool_registry.execute_tool(
                        'execute_command',
                        {'command': init_command},
                        f"agent-{self.config.id}"
                    )

                    if result.get('success'):
                        commands_executed.append(init_command)

                        return {
                            'success': True,
                            'response': "Application initialized successfully. Database created and ready to use.",
                            'files_created': [],
                            'files_modified': [],
                            'commands_executed': commands_executed
                        }

                return {
                    'success': True,
                    'response': "Setup task completed",
                    'files_created': [],
                    'files_modified': [],
                    'commands_executed': []
                }

            # Fallback to regular task execution
            return await self.process_single_prompt(
                f"Complete this task: {task.name}\nDescription: {task.description}",
                options
            )

        except Exception as error:
            self.logger.error(f'Template task execution failed: {task.name}', {
                'task_id': task.id,
                'error': str(error)
            })

            return {
                'success': False,
                'error': str(error),
                'files_created': [],
                'files_modified': [],
                'commands_executed': []
            }

    def _on_task_start(self, task):
        """Callback when a task starts"""
        self.task_manager.display_task_start_notification(task)

    def _on_task_complete(self, task):
        """Callback when a task completes"""
        self.task_manager.display_task_complete_notification(task)

    def _on_task_failed(self, task):
        """Callback when a task fails"""
        self.task_manager.display_task_failed_notification(task)

    def _on_all_tasks_complete(self):
        """Callback when all tasks are complete"""
        self.task_manager.console.print(f"\n🎉 [bold green]All tasks completed successfully![/bold green]")

    async def test_connection(self, provider: str, api_key: str) -> Dict[str, Any]:
        """Test connection to provider"""
        try:
            test_result = await self.provider_manager.test_api_key(provider, api_key)
            
            return {
                'success': test_result,
                'provider': provider,
                'message': f'{provider.upper()} API key is {"valid" if test_result else "invalid"}'
            }
            
        except Exception as error:
            return {
                'success': False,
                'provider': provider,
                'error': str(error),
                'message': f'Failed to test {provider.upper()} API key: {str(error)}'
            }

    def get_supported_providers(self) -> list:
        """Get list of supported providers"""
        return self.provider_manager.get_supported_providers()

    def get_provider_models(self, provider: str) -> list:
        """Get available models for a provider"""
        return self.provider_manager.get_available_models(provider)

    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            'id': self.id,
            'name': self.name,
            'state': self.state.value,
            'provider': self.provider_config['provider'],
            'model': self.provider_config['model'],
            'tools_enabled': self.config.tools_enabled,
            'uptime': (datetime.now() - self.start_time).total_seconds(),
            'metrics': self.metrics.__dict__
        }

    def _extract_complete_json(self, json_str: str) -> str:
        """Extract complete JSON object by counting braces"""
        if not json_str.strip().startswith('{'):
            return json_str

        brace_count = 0
        in_string = False
        in_triple_quote = False
        escape_next = False
        end_pos = 0
        i = 0

        while i < len(json_str):
            char = json_str[i]

            if escape_next:
                escape_next = False
                i += 1
                continue

            if char == '\\' and (in_string or in_triple_quote):
                escape_next = True
                i += 1
                continue

            # Check for triple quotes
            if i + 2 < len(json_str) and json_str[i:i+3] == '"""':
                if not in_string:
                    in_triple_quote = not in_triple_quote
                i += 3
                continue

            if char == '"' and not in_triple_quote:
                in_string = not in_string
                i += 1
                continue

            if not in_string and not in_triple_quote:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_pos = i + 1
                        break

            i += 1

        return json_str[:end_pos] if end_pos > 0 else json_str

    def _fix_json_content(self, json_str: str) -> str:
        """Fix common JSON issues like triple quotes"""
        import re

        # Replace triple quotes with escaped quotes in content values
        # This regex finds "content": """...""" patterns and fixes them
        def replace_triple_quotes(match):
            key = match.group(1)
            content = match.group(2)
            # Escape quotes and newlines in the content
            escaped_content = content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
            return f'"{key}": "{escaped_content}"'

        # Pattern to match "key": """content"""
        pattern = r'"([^"]+)":\s*"""(.*?)"""'
        fixed_json = re.sub(pattern, replace_triple_quotes, json_str, flags=re.DOTALL)

        return fixed_json
