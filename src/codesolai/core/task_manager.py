"""
Task Management System for CodeSolAI
Provides task decomposition, tracking, and progress management similar to Augment Agent
"""

import uuid
import asyncio
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.text import Text

from .logger import Logger


class TaskState(Enum):
    """Task execution states"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Individual task representation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    state: TaskState = TaskState.NOT_STARTED
    parent_id: Optional[str] = None
    subtasks: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    progress: float = 0.0  # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def duration(self) -> Optional[float]:
        """Get task duration in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            return (datetime.now() - self.started_at).total_seconds()
        return None
    
    def is_root_task(self) -> bool:
        """Check if this is a root task"""
        return self.parent_id is None
    
    def has_subtasks(self) -> bool:
        """Check if task has subtasks"""
        return len(self.subtasks) > 0


@dataclass 
class TaskExecutionContext:
    """Context for task execution"""
    task_id: str
    agent_config: Dict[str, Any]
    tools_enabled: bool = True
    auto_approve: bool = True
    max_retries: int = 3
    timeout: Optional[float] = None
    callbacks: Dict[str, Callable] = field(default_factory=dict)


class TaskManager:
    """Manages task decomposition, execution, and progress tracking"""
    
    def __init__(self, logger: Logger, console: Optional[Console] = None):
        self.logger = logger
        self.console = console or Console()
        self.tasks: Dict[str, Task] = {}
        self.execution_order: List[str] = []
        self.current_task_id: Optional[str] = None
        self.progress_display: Optional[Progress] = None
        self.progress_tasks: Dict[str, TaskID] = {}
        
        # Callbacks
        self.on_task_start: Optional[Callable] = None
        self.on_task_complete: Optional[Callable] = None
        self.on_task_failed: Optional[Callable] = None
        self.on_all_complete: Optional[Callable] = None
        
        self.logger.debug("Task manager initialized")
    
    def create_task(self, name: str, description: str, parent_id: Optional[str] = None, 
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new task"""
        task = Task(
            name=name,
            description=description,
            parent_id=parent_id,
            metadata=metadata or {}
        )
        
        self.tasks[task.id] = task
        
        # Add to parent's subtasks if applicable
        if parent_id and parent_id in self.tasks:
            self.tasks[parent_id].subtasks.append(task.id)
        
        # Add to execution order if it's a root task or leaf task
        if not parent_id or not task.has_subtasks():
            self.execution_order.append(task.id)
        
        self.logger.info(f"Task created: {name}", {
            "task_id": task.id,
            "parent_id": parent_id,
            "has_parent": parent_id is not None
        })
        
        return task.id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def get_root_tasks(self) -> List[Task]:
        """Get all root tasks"""
        return [task for task in self.tasks.values() if task.is_root_task()]
    
    def get_subtasks(self, parent_id: str) -> List[Task]:
        """Get all subtasks of a parent task"""
        parent = self.tasks.get(parent_id)
        if not parent:
            return []
        
        return [self.tasks[subtask_id] for subtask_id in parent.subtasks 
                if subtask_id in self.tasks]
    
    def get_next_task(self) -> Optional[Task]:
        """Get the next task to execute"""
        for task_id in self.execution_order:
            task = self.tasks.get(task_id)
            if task and task.state == TaskState.NOT_STARTED:
                return task
        return None
    
    def start_task(self, task_id: str) -> bool:
        """Start executing a task"""
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        if task.state != TaskState.NOT_STARTED:
            return False
        
        task.state = TaskState.IN_PROGRESS
        task.started_at = datetime.now()
        self.current_task_id = task_id
        
        self.logger.info(f"Task started: {task.name}", {"task_id": task_id})
        
        if self.on_task_start:
            self.on_task_start(task)
        
        return True
    
    def complete_task(self, task_id: str, result: Optional[Dict[str, Any]] = None) -> bool:
        """Mark a task as completed"""
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        task.state = TaskState.COMPLETED
        task.completed_at = datetime.now()
        task.result = result
        task.progress = 1.0
        
        if self.current_task_id == task_id:
            self.current_task_id = None
        
        self.logger.info(f"Task completed: {task.name}", {
            "task_id": task_id,
            "duration": task.duration()
        })
        
        if self.on_task_complete:
            self.on_task_complete(task)
        
        # Check if all tasks are complete
        if self._all_tasks_complete():
            if self.on_all_complete:
                self.on_all_complete()
        
        return True
    
    def fail_task(self, task_id: str, error: str) -> bool:
        """Mark a task as failed"""
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        task.state = TaskState.FAILED
        task.completed_at = datetime.now()
        task.error = error
        
        if self.current_task_id == task_id:
            self.current_task_id = None
        
        self.logger.error(f"Task failed: {task.name}", {
            "task_id": task_id,
            "error": error,
            "duration": task.duration()
        })
        
        if self.on_task_failed:
            self.on_task_failed(task)
        
        return True
    
    def _all_tasks_complete(self) -> bool:
        """Check if all tasks are complete"""
        for task in self.tasks.values():
            if task.state not in [TaskState.COMPLETED, TaskState.CANCELLED]:
                return False
        return True
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get overall progress summary"""
        total_tasks = len(self.tasks)
        completed_tasks = len([t for t in self.tasks.values() if t.state == TaskState.COMPLETED])
        failed_tasks = len([t for t in self.tasks.values() if t.state == TaskState.FAILED])
        in_progress_tasks = len([t for t in self.tasks.values() if t.state == TaskState.IN_PROGRESS])

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "progress_percentage": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "current_task": self.get_task(self.current_task_id) if self.current_task_id else None
        }

    def display_progress(self, show_detailed: bool = True) -> None:
        """Display current progress in a formatted table"""
        summary = self.get_progress_summary()

        if show_detailed:
            # Create progress table
            table = Table(title="📋 Task Progress", show_header=True, header_style="bold magenta")
            table.add_column("Task", style="cyan", no_wrap=True, width=25)
            table.add_column("Status", style="green", width=15)
            table.add_column("Duration", style="yellow", width=10)
            table.add_column("Description", style="white")

            # Add tasks to table in execution order
            for task_id in self.execution_order:
                task = self.tasks.get(task_id)
                if not task:
                    continue

                status_emoji = {
                    TaskState.NOT_STARTED: "⏳",
                    TaskState.IN_PROGRESS: "🔄",
                    TaskState.COMPLETED: "✅",
                    TaskState.FAILED: "❌",
                    TaskState.CANCELLED: "🚫"
                }.get(task.state, "❓")

                duration_str = ""
                if task.duration():
                    duration_str = f"{task.duration():.1f}s"

                # Highlight current task
                task_name = task.name
                if task.state == TaskState.IN_PROGRESS:
                    task_name = f"[bold yellow]{task.name}[/bold yellow]"

                table.add_row(
                    task_name,
                    f"{status_emoji} {task.state.value.replace('_', ' ').title()}",
                    duration_str,
                    task.description[:60] + "..." if len(task.description) > 60 else task.description
                )

            self.console.print(table)

        # Display summary panel
        progress_bar = "█" * int(summary['progress_percentage'] / 5) + "░" * (20 - int(summary['progress_percentage'] / 5))
        summary_text = f"""
📊 [bold]Execution Summary[/bold]
   Total Tasks: {summary['total_tasks']}
   Completed: {summary['completed_tasks']} ✅  Failed: {summary['failed_tasks']} ❌  In Progress: {summary['in_progress_tasks']} 🔄

🔥 [bold]Progress: {summary['progress_percentage']:.1f}%[/bold]
   [{progress_bar}] {summary['completed_tasks']}/{summary['total_tasks']}
        """.strip()

        summary_panel = Panel(summary_text, title="📈 Status Overview", border_style="blue", padding=(0, 1))
        self.console.print(summary_panel)

        # Show current task if any
        if summary['current_task']:
            current_task = summary['current_task']
            current_panel = Panel(
                f"🎯 [bold cyan]{current_task.name}[/bold cyan]\n💭 {current_task.description}",
                title="🔄 Current Task",
                border_style="green",
                padding=(0, 1)
            )
            self.console.print(current_panel)

    def display_compact_progress(self) -> None:
        """Display a compact progress indicator"""
        summary = self.get_progress_summary()
        progress_pct = summary['progress_percentage']

        # Create progress bar
        filled = int(progress_pct / 5)
        bar = "█" * filled + "░" * (20 - filled)

        status_text = f"[{bar}] {progress_pct:.1f}% ({summary['completed_tasks']}/{summary['total_tasks']})"

        if summary['current_task']:
            current_name = summary['current_task'].name
            status_text += f" | 🔄 {current_name}"

        self.console.print(f"📊 {status_text}")

    def display_task_start_notification(self, task) -> None:
        """Display notification when a task starts"""
        self.console.print(f"\n🚀 [bold cyan]Starting Task {self._get_task_number(task.id)}/{len(self.tasks)}:[/bold cyan] [bold white]{task.name}[/bold white]")
        self.console.print(f"   💡 [dim]{task.description}[/dim]")

        # Show compact progress
        self.display_compact_progress()

    def display_task_complete_notification(self, task) -> None:
        """Display notification when a task completes"""
        duration = task.duration()
        duration_str = f" in {duration:.1f}s" if duration else ""

        self.console.print(f"✅ [bold green]Completed:[/bold green] {task.name}{duration_str}")

        # Show updated progress
        summary = self.get_progress_summary()
        progress_pct = summary['progress_percentage']
        self.console.print(f"   📈 [dim]Overall Progress: {progress_pct:.1f}% ({summary['completed_tasks']}/{summary['total_tasks']} tasks complete)[/dim]")

    def display_task_failed_notification(self, task) -> None:
        """Display notification when a task fails"""
        self.console.print(f"❌ [bold red]Task Failed:[/bold red] {task.name}")
        if task.error:
            self.console.print(f"   🚨 [dim red]Error: {task.error}[/dim red]")

        # Show options for handling failure
        self.console.print(f"   ⚠️  [dim yellow]Continuing with remaining tasks...[/dim yellow]")

    def _get_task_number(self, task_id: str) -> int:
        """Get the sequential number of a task in execution order"""
        try:
            return self.execution_order.index(task_id) + 1
        except ValueError:
            return 0

    def display_completion_summary(self) -> Dict[str, Any]:
        """Display final completion summary and return detailed summary data"""
        summary = self.get_progress_summary()

        # Calculate total duration
        total_duration = 0
        successful_tasks = []
        failed_tasks = []

        for task in self.tasks.values():
            if task.duration():
                total_duration += task.duration()

            if task.state == TaskState.COMPLETED:
                successful_tasks.append(task)
            elif task.state == TaskState.FAILED:
                failed_tasks.append(task)

        # Collect file and command information from task results
        files_created = []
        files_modified = []
        commands_executed = []
        directories_created = []

        for task in self.tasks.values():
            if task.result:
                if 'files_created' in task.result:
                    files_created.extend(task.result['files_created'])
                if 'files_modified' in task.result:
                    files_modified.extend(task.result['files_modified'])
                if 'commands_executed' in task.result:
                    commands_executed.extend(task.result['commands_executed'])
                if 'directories_created' in task.result:
                    directories_created.extend(task.result['directories_created'])

        # Remove duplicates
        files_created = list(set(files_created))
        files_modified = list(set(files_modified))
        commands_executed = list(set(commands_executed))
        directories_created = list(set(directories_created))

        # Create detailed completion summary
        completion_text = f"""
🎉 [bold green]Autonomous Execution Complete![/bold green] 🎉

📊 [bold]Execution Summary:[/bold]
   • Total Tasks: {summary['total_tasks']}
   • Completed Successfully: {summary['completed_tasks']} ✅
   • Failed: {summary['failed_tasks']} ❌
   • Total Execution Time: {total_duration:.1f} seconds
   • Success Rate: {(summary['completed_tasks'] / summary['total_tasks'] * 100):.1f}%

📁 [bold]Files & Directories Created:[/bold]"""

        if directories_created:
            completion_text += f"\n   📂 Directories: {len(directories_created)}"
            for directory in directories_created[:3]:
                completion_text += f"\n      • {directory}/"
            if len(directories_created) > 3:
                completion_text += f"\n      • ... and {len(directories_created) - 3} more directories"

        if files_created:
            completion_text += f"\n   📝 Files Created: {len(files_created)}"
            for file_path in files_created[:8]:  # Show first 8
                completion_text += f"\n      • {file_path}"
            if len(files_created) > 8:
                completion_text += f"\n      • ... and {len(files_created) - 8} more files"

        if files_modified:
            completion_text += f"\n   ✏️  Files Modified: {len(files_modified)}"

        if commands_executed:
            completion_text += f"\n   ⚡ Commands Executed: {len(commands_executed)}"
            for command in commands_executed[:3]:
                completion_text += f"\n      • {command}"
            if len(commands_executed) > 3:
                completion_text += f"\n      • ... and {len(commands_executed) - 3} more commands"

        # Add task breakdown
        if successful_tasks:
            completion_text += f"\n\n✅ [bold]Completed Tasks:[/bold]"
            for task in successful_tasks:
                duration_str = f" ({task.duration():.1f}s)" if task.duration() else ""
                completion_text += f"\n   • {task.name}{duration_str}"

        if failed_tasks:
            completion_text += f"\n\n❌ [bold]Failed Tasks:[/bold]"
            for task in failed_tasks:
                completion_text += f"\n   • {task.name}"
                if task.error:
                    completion_text += f"\n     Error: {task.error[:100]}..."

        # Add next steps or usage instructions
        project_type = None
        for task in self.tasks.values():
            if task.metadata.get('project_type'):
                project_type = task.metadata['project_type']
                break

        if project_type == 'flask_web_app' and summary['failed_tasks'] == 0:
            completion_text += f"""

🚀 [bold]Next Steps:[/bold]
   1. Install dependencies: [cyan]pip install -r requirements.txt[/cyan]
   2. Run the application: [cyan]python app.py[/cyan]
   3. Open your browser to: [cyan]http://localhost:5000[/cyan]
   4. Register a new account or login to test authentication
"""

        completion_text += "\n\n✨ [bold green]All requested tasks have been completed successfully![/bold green] ✨"

        completion_panel = Panel(
            completion_text,
            title="🏆 Autonomous Execution Complete",
            border_style="green",
            padding=(1, 2)
        )

        self.console.print("\n")
        self.console.print(completion_panel)
        self.console.print("\n")

        # Return detailed summary data
        return {
            'total_tasks': summary['total_tasks'],
            'completed_tasks': summary['completed_tasks'],
            'failed_tasks': summary['failed_tasks'],
            'success_rate': (summary['completed_tasks'] / summary['total_tasks'] * 100) if summary['total_tasks'] > 0 else 0,
            'total_duration': total_duration,
            'files_created': files_created,
            'files_modified': files_modified,
            'commands_executed': commands_executed,
            'directories_created': directories_created,
            'successful_tasks': [{'name': t.name, 'duration': t.duration()} for t in successful_tasks],
            'failed_tasks': [{'name': t.name, 'error': t.error} for t in failed_tasks],
            'project_type': project_type
        }

    async def decompose_task(self, main_request: str, agent_config: Dict[str, Any]) -> List[str]:
        """Decompose a complex request into subtasks using AI with enhanced file creation support"""
        from ..providers.provider_manager import ProviderManager
        from .file_creation_helper import FileCreationHelper

        # Initialize provider manager with empty config (it will use defaults)
        provider_manager = ProviderManager({})
        file_helper = FileCreationHelper()

        # Check if this is a known project type that we have templates for
        project_type = self._detect_project_type(main_request)
        self.logger.info(f"Detected project type: {project_type}")

        if project_type:
            # Use template-based task generation for known project types
            self.logger.info(f"Using template-based task generation for {project_type}")
            return self._create_template_based_tasks(project_type, main_request, file_helper)

        # Fall back to AI-based decomposition for unknown project types
        decomposition_prompt = f"""
You are an expert task decomposition agent. Break down the following request into specific, actionable subtasks that can be executed sequentially.

Request: {main_request}

IMPORTANT GUIDELINES:
1. Create tasks that result in complete, functional files (not empty placeholders)
2. Include all necessary configuration files (requirements.txt, package.json, etc.)
3. Consider directory structure creation
4. Include database setup if needed
5. Add styling and frontend assets
6. Include error handling and logging setup
7. Consider deployment preparation

Please provide a detailed breakdown with:
- Clear, specific task names (suitable for progress tracking)
- Brief descriptions of what each task accomplishes
- Logical order of execution
- Focus on creating COMPLETE, WORKING implementations

Format your response as a JSON array of objects with 'name' and 'description' fields:
[
  {{"name": "Create project directory structure", "description": "Set up the basic directory structure for the project"}},
  {{"name": "Create main application file", "description": "Create the main application file with complete implementation"}},
  {{"name": "Create configuration files", "description": "Create requirements.txt, config files, and other necessary configuration"}},
  ...
]

Focus on creating comprehensive, executable tasks that will fully complete the request with working code.
"""

        try:
            provider = agent_config.get('provider', 'claude')
            api_key = agent_config.get('api_key')

            if not api_key:
                self.logger.error("No API key provided for task decomposition")
                return []

            self.logger.info(f"Calling {provider} for task decomposition")
            response = await provider_manager.call(
                provider, api_key, decomposition_prompt, {
                    'temperature': 0.3,
                    'max_tokens': 2000
                }
            )

            self.logger.info(f"Received response from {provider}: {len(response)} characters")

            # Parse the JSON response
            import json
            import re

            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                self.logger.info(f"Found JSON in response: {json_str[:200]}...")

                try:
                    tasks_data = json.loads(json_str)
                    self.logger.info(f"Successfully parsed {len(tasks_data)} tasks from JSON")

                    # Create tasks
                    task_ids = []
                    for i, task_data in enumerate(tasks_data):
                        task_id = self.create_task(
                            name=task_data.get('name', f'Task {i+1}'),
                            description=task_data.get('description', 'No description'),
                            metadata={'auto_generated': True}
                        )
                        task_ids.append(task_id)

                    self.logger.info(f"Decomposed request into {len(task_ids)} subtasks")
                    return task_ids

                except json.JSONDecodeError as json_error:
                    self.logger.error(f"JSON parsing failed: {json_error}")
                    self.logger.error(f"JSON string was: {json_str}")
                    return []
            else:
                self.logger.error("Could not find JSON array in response")
                self.logger.error(f"Full response was: {response}")
                return []

        except Exception as error:
            self.logger.error(f"Task decomposition failed: {error}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    def _detect_project_type(self, request: str) -> Optional[str]:
        """Detect project type from the request"""
        request_lower = request.lower()

        # Flask web app detection
        if any(keyword in request_lower for keyword in ['flask', 'web app', 'web application', 'authentication', 'login']):
            if 'flask' in request_lower or 'python' in request_lower:
                return 'flask_web_app'

        return None

    def _create_template_based_tasks(self, project_type: str, request: str, file_helper) -> List[str]:
        """Create tasks based on project templates"""
        self.logger.info(f"Using template-based task creation for project type: {project_type}")

        # Get file creation tasks from template
        file_tasks = file_helper.generate_file_creation_tasks(project_type)

        task_ids = []

        # Create directory structure task first
        dir_task_id = self.create_task(
            name="Create project directory structure",
            description="Set up the basic directory structure and create necessary folders",
            metadata={'template_based': True, 'project_type': project_type}
        )
        task_ids.append(dir_task_id)

        # Create file creation tasks
        for file_task in file_tasks:
            task_id = self.create_task(
                name=file_task['name'],
                description=file_task['description'],
                metadata={
                    'template_based': True,
                    'project_type': project_type,
                    'file_path': file_task['file_path'],
                    'file_content': file_task['content']
                }
            )
            task_ids.append(task_id)

        # Add final setup task
        setup_task_id = self.create_task(
            name="Initialize and test the application",
            description="Run initial setup commands and verify the application works correctly",
            metadata={'template_based': True, 'project_type': project_type}
        )
        task_ids.append(setup_task_id)

        self.logger.info(f"Created {len(task_ids)} template-based tasks")
        return task_ids
