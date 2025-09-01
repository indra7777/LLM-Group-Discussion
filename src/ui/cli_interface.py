"""Command-line interface for the multi-agent discussion system."""

import os
import sys
from typing import List, Optional
from colorama import init, Fore, Style, Back
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.discussion_manager import DiscussionManager

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Initialize rich console
console = Console()


class CLIInterface:
    """Command-line interface for multi-agent discussions."""
    
    def __init__(self, demo_mode: bool = False):
        self.discussion_manager = DiscussionManager(demo_mode=demo_mode)
        self.running = True
        self.demo_mode = demo_mode
        
        # Color mappings for agents
        self.agent_colors = {
            "Dr. Skeptic": Fore.RED,
            "Dr. Synthesis": Fore.GREEN, 
            "Dr. Data": Fore.BLUE,
            "Dr. Discovery": Fore.MAGENTA
        }
    
    def display_welcome(self):
        """Display welcome message and instructions."""
        mode_text = "[yellow]DEMO MODE[/yellow] - " if self.demo_mode else ""
        console.print(Panel.fit(
            f"[bold cyan]Multi-Agent Discussion System[/bold cyan]\n\n"
            f"{mode_text}Welcome to the collaborative AI research platform!\n\n"
            "[yellow]Available Commands:[/yellow]\n"
            "• start <topic> - Start a new discussion\n"
            "• speak <message> - Add your message to the discussion\n"  
            "• next - Let agents respond\n"
            "• research <topic> - Research a topic using web search\n"
            "• status - Show discussion status\n"
            "• usage - Show API usage and costs\n"
            "• summary - Get discussion summary\n"
            "• messages - Show recent messages\n"
            "• save - Save current conversation\n"
            "• list - List saved conversations\n"
            "• load <filename> - Load a conversation\n"
            "• search <query> - Search saved conversations\n"
            "• analyze <filename> - Analyze conversation quality\n"
            "• end - End current discussion\n"
            "• help - Show this help\n"
            "• quit - Exit the system",
            title="Welcome",
            border_style="cyan"
        ))
    
    def display_agents(self):
        """Display information about available agents."""
        table = Table(title="Discussion Agents")
        table.add_column("Agent", style="cyan", no_wrap=True)
        table.add_column("Role", style="magenta")
        table.add_column("Focus", style="green")
        
        agents_info = [
            ("Dr. Skeptic", "Critical Analyst", "Questions assumptions, identifies flaws"),
            ("Dr. Synthesis", "Integrative Thinker", "Connects ideas, builds consensus"),
            ("Dr. Data", "Evidence-Based Researcher", "Provides facts and data"),
            ("Dr. Discovery", "Creative Visionary", "Generates novel perspectives")
        ]
        
        for agent, role, focus in agents_info:
            table.add_row(agent, role, focus)
        
        console.print(table)
    
    def format_message(self, message: dict) -> str:
        """Format a message for display."""
        speaker = message["speaker"]
        content = message["content"]
        msg_type = message["type"]
        timestamp = message["timestamp"].strftime("%H:%M:%S")
        
        if msg_type == "system":
            return f"{Fore.YELLOW}[{timestamp}] SYSTEM: {content}{Style.RESET_ALL}"
        elif msg_type == "human":
            return f"{Fore.CYAN}[{timestamp}] {speaker}: {content}{Style.RESET_ALL}"
        elif msg_type == "agent":
            color = self.agent_colors.get(speaker, Fore.WHITE)
            return f"{color}[{timestamp}] {speaker}: {content}{Style.RESET_ALL}"
        else:
            return f"[{timestamp}] {speaker}: {content}"
    
    def display_messages(self, messages: List[dict], limit: int = 10):
        """Display recent messages."""
        recent_messages = messages[-limit:] if len(messages) > limit else messages
        
        if not recent_messages:
            console.print("[yellow]No messages yet.[/yellow]")
            return
        
        console.print("\n[bold]Recent Discussion:[/bold]")
        for message in recent_messages:
            formatted = self.format_message(message)
            print(formatted)
    
    def handle_start_command(self, args: List[str]):
        """Handle the start discussion command."""
        if not args:
            console.print("[red]Please provide a topic. Usage: start <topic>[/red]")
            return
        
        topic = " ".join(args)
        session = self.discussion_manager.start_discussion(topic)
        
        console.print(Panel(
            f"[green]Discussion started![/green]\n\n"
            f"Topic: {topic}\n"
            f"Session ID: {session.session_id}",
            title="New Discussion",
            border_style="green"
        ))
        
        self.display_agents()
        console.print("\n[yellow]Type 'next' to let agents start the discussion, or 'speak <message>' to contribute.[/yellow]")
    
    def handle_speak_command(self, args: List[str]):
        """Handle user speaking in the discussion."""
        if not self.discussion_manager.current_session:
            console.print("[red]No active discussion. Start one with 'start <topic>'[/red]")
            return
        
        if not args:
            console.print("[red]Please provide a message. Usage: speak <message>[/red]")
            return
        
        message = " ".join(args)
        username = "Human"  # TODO: Allow customizable username
        
        self.discussion_manager.add_human_message(username, message)
        console.print(f"[green]Your message added to the discussion.[/green]")
    
    def handle_next_command(self):
        """Handle letting agents respond."""
        if not self.discussion_manager.current_session:
            console.print("[red]No active discussion. Start one with 'start <topic>'[/red]")
            return
        
        if not self.discussion_manager.should_continue_discussion():
            console.print("[yellow]Discussion has reached its limit. Type 'end' to conclude.[/yellow]")
            return
        
        console.print("[blue]Agents are thinking...[/blue]")
        
        # Generate agent responses
        responses = self.discussion_manager.generate_agent_responses()
        
        if responses:
            console.print(f"\n[green]{len(responses)} agent(s) responded:[/green]")
            for response in responses:
                formatted = self.format_message(response)
                print(formatted)
        else:
            console.print("[yellow]No agent responses generated.[/yellow]")
        
        # Advance round
        self.discussion_manager.advance_round()
    
    def handle_status_command(self):
        """Handle status display."""
        status = self.discussion_manager.get_session_status()
        
        if status["status"] == "no_active_session":
            console.print("[yellow]No active discussion session.[/yellow]")
            return
        
        table = Table(title="Discussion Status")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Status", status["status"])
        table.add_row("Topic", status["topic"])
        table.add_row("Round", str(status["round"]))
        table.add_row("Total Messages", str(status["total_messages"]))
        table.add_row("Human Participants", ", ".join(status["human_participants"]) or "None")
        
        console.print(table)
        
        # Agent participation
        participation_table = Table(title="Agent Participation")
        participation_table.add_column("Agent", style="cyan")
        participation_table.add_column("Messages", style="white")
        
        for agent, count in status["agent_participation"].items():
            participation_table.add_row(agent, str(count))
        
        console.print(participation_table)
    
    def handle_summary_command(self):
        """Handle summary display."""
        if not self.discussion_manager.current_session:
            console.print("[red]No active discussion to summarize.[/red]")
            return
        
        summary = self.discussion_manager.generate_discussion_summary()
        
        console.print(Panel(
            summary,
            title="Discussion Summary",
            border_style="blue"
        ))
    
    def handle_end_command(self):
        """Handle ending the discussion."""
        if not self.discussion_manager.current_session:
            console.print("[yellow]No active discussion to end.[/yellow]")
            return
        
        result = self.discussion_manager.end_discussion()
        
        console.print(Panel(
            f"[green]Discussion ended successfully![/green]\n\n"
            f"Topic: {result['topic']}\n"
            f"Total Messages: {result['total_messages']}\n"
            f"Rounds: {result['rounds']}\n"
            f"Summary: {result['summary']}",
            title="Discussion Complete",
            border_style="green"
        ))
    
    def handle_research_command(self, args: List[str]):
        """Handle research command."""
        if not args:
            console.print("[red]Please provide a research topic. Usage: research <topic>[/red]")
            return
        
        topic = " ".join(args)
        
        try:
            # Import research tool
            from src.utils.research_tool import research_tool, quick_research_summary
            from src.agents.research_agent import ResearchAgent
            
            # Check if research tool is configured
            if not research_tool.is_configured():
                console.print(Panel(
                    "[red]Research tool not configured![/red]\n\n" + 
                    research_tool.get_config_instructions(),
                    title="Research Configuration Needed",
                    border_style="red"
                ))
                return
            
            console.print(f"[yellow]🔍 Researching: {topic}...[/yellow]")
            
            # Perform research
            summary = quick_research_summary(topic, max_sources=3)
            
            # Display results
            console.print(Panel(
                summary,
                title=f"Research Results: {topic}",
                border_style="green"
            ))
            
            # If there's an active discussion, offer to add research to it
            if self.discussion_manager.current_session:
                console.print("\n[yellow]Add this research to the current discussion? (y/n)[/yellow]")
                response = input("> ").strip().lower()
                if response in ['y', 'yes']:
                    research_message = f"Research findings for '{topic}':\n\n{summary}"
                    self.discussion_manager.add_human_message("Research Assistant", research_message)
                    console.print("[green]Research added to discussion![/green]")
        
        except ImportError as e:
            console.print(f"[red]Research functionality not available: {e}[/red]")
        except Exception as e:
            console.print(f"[red]Research failed: {e}[/red]")
    
    def handle_help_command(self):
        """Display help information."""
        self.display_welcome()
    
    def run(self):
        """Main CLI loop."""
        self.display_welcome()
        
        while self.running:
            try:
                # Get user input
                user_input = input(f"\n{Fore.GREEN}> {Style.RESET_ALL}").strip()
                
                if not user_input:
                    continue
                
                # Parse command
                parts = user_input.split()
                command = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                # Handle commands
                if command == "quit" or command == "exit":
                    self.running = False
                    console.print("[yellow]Goodbye![/yellow]")
                
                elif command == "start":
                    self.handle_start_command(args)
                
                elif command == "speak":
                    self.handle_speak_command(args)
                
                elif command == "next":
                    self.handle_next_command()
                
                elif command == "status":
                    self.handle_status_command()
                
                elif command == "summary":
                    self.handle_summary_command()
                
                elif command == "end":
                    self.handle_end_command()
                
                elif command == "help":
                    self.handle_help_command()
                
                elif command == "research":
                    self.handle_research_command(args)
                
                elif command == "messages":
                    if self.discussion_manager.current_session:
                        self.display_messages(self.discussion_manager.current_session.messages)
                    else:
                        console.print("[yellow]No active discussion.[/yellow]")
                
                else:
                    console.print(f"[red]Unknown command: {command}. Type 'help' for available commands.[/red]")
            
            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'quit' to exit.[/yellow]")
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")


if __name__ == "__main__":
    cli = CLIInterface()
    cli.run()