"""Simple command-line interface without external UI dependencies."""

import os
import sys
from typing import List

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.discussion_manager import DiscussionManager


class SimpleCLI:
    """Simple command-line interface for multi-agent discussions."""
    
    def __init__(self, demo_mode: bool = False):
        self.discussion_manager = DiscussionManager(demo_mode=demo_mode)
        self.running = True
        self.demo_mode = demo_mode
    
    def display_welcome(self):
        """Display welcome message and instructions."""
        mode_text = "[DEMO MODE] " if self.demo_mode else ""
        print("=" * 60)
        print(f"    Multi-Agent Discussion System")
        print(f"    {mode_text}Collaborative AI Research Platform")
        print("=" * 60)
        print()
        print("Available Commands:")
        print("  start <topic>     - Start a new discussion")
        print("  speak <message>   - Add your message to the discussion")
        print("  next              - Let agents respond")
        print("  status            - Show discussion status")
        print("  usage             - Show API usage and costs")
        print("  summary           - Get discussion summary")
        print("  messages          - Show recent messages")
        print("  save              - Save current conversation")
        print("  list              - List saved conversations")
        print("  load <filename>   - Load a conversation")
        print("  search <query>    - Search saved conversations")
        print("  analyze <filename>- Analyze a conversation")
        print("  end               - End current discussion")
        print("  help              - Show this help")
        print("  quit              - Exit the system")
        print()
    
    def display_agents(self):
        """Display information about available agents."""
        print("Discussion Agents:")
        print("  Dr. Skeptic       - Critical Analyst - Questions assumptions")
        print("  Dr. Synthesis     - Integrative Thinker - Connects ideas")
        print("  Dr. Data          - Evidence Researcher - Provides facts")
        print("  Dr. Discovery     - Creative Visionary - Novel perspectives")
        print()
    
    def format_message(self, message: dict) -> str:
        """Format a message for display."""
        speaker = message["speaker"]
        content = message["content"]
        msg_type = message["type"]
        timestamp = message["timestamp"].strftime("%H:%M:%S")
        
        if msg_type == "system":
            return f"[{timestamp}] SYSTEM: {content}"
        elif msg_type == "human":
            return f"[{timestamp}] {speaker}: {content}"
        elif msg_type == "agent":
            return f"[{timestamp}] {speaker}: {content}"
        else:
            return f"[{timestamp}] {speaker}: {content}"
    
    def display_messages(self, messages: List[dict], limit: int = 10):
        """Display recent messages."""
        recent_messages = messages[-limit:] if len(messages) > limit else messages
        
        if not recent_messages:
            print("No messages yet.")
            return
        
        print("\nRecent Discussion:")
        print("-" * 50)
        for message in recent_messages:
            formatted = self.format_message(message)
            print(formatted)
        print("-" * 50)
    
    def handle_start_command(self, args: List[str]):
        """Handle the start discussion command."""
        if not args:
            print("Please provide a topic. Usage: start <topic>")
            return
        
        topic = " ".join(args)
        session = self.discussion_manager.start_discussion(topic)
        
        print(f"\nDiscussion started!")
        print(f"Topic: {topic}")
        print(f"Session ID: {session.session_id}")
        print()
        
        self.display_agents()
        print("Type 'next' to let agents start the discussion, or 'speak <message>' to contribute.")
    
    def handle_speak_command(self, args: List[str]):
        """Handle user speaking in the discussion."""
        if not self.discussion_manager.current_session:
            print("No active discussion. Start one with 'start <topic>'")
            return
        
        if not args:
            print("Please provide a message. Usage: speak <message>")
            return
        
        message = " ".join(args)
        username = "Human"
        
        self.discussion_manager.add_human_message(username, message)
        print("Your message added to the discussion.")
    
    def handle_next_command(self):
        """Handle letting agents respond."""
        if not self.discussion_manager.current_session:
            print("No active discussion. Start one with 'start <topic>'")
            return
        
        if not self.discussion_manager.should_continue_discussion():
            print("Discussion has reached its limit. Type 'end' to conclude.")
            return
        
        print("Agents are thinking...")
        
        # Generate agent responses
        responses = self.discussion_manager.generate_agent_responses()
        
        if responses:
            print(f"\n{len(responses)} agent(s) responded:")
            for response in responses:
                formatted = self.format_message(response)
                print(formatted)
        else:
            print("No agent responses generated.")
        
        # Advance round
        self.discussion_manager.advance_round()
    
    def handle_status_command(self):
        """Handle status display."""
        status = self.discussion_manager.get_session_status()
        
        if status["status"] == "no_active_session":
            print("No active discussion session.")
            return
        
        print("\nDiscussion Status:")
        print(f"  Status: {status['status']}")
        print(f"  Topic: {status['topic']}")
        print(f"  Round: {status['round']}")
        print(f"  Total Messages: {status['total_messages']}")
        print(f"  Human Participants: {', '.join(status['human_participants']) or 'None'}")
        
        print("\nAgent Participation:")
        for agent, count in status["agent_participation"].items():
            print(f"  {agent}: {count} messages")
    
    def handle_summary_command(self):
        """Handle summary display."""
        if not self.discussion_manager.current_session:
            print("No active discussion to summarize.")
            return
        
        summary = self.discussion_manager.generate_discussion_summary()
        print(f"\nDiscussion Summary:")
        print(f"{summary}")
    
    def handle_usage_command(self):
        """Handle API usage display."""
        if self.demo_mode:
            print("\nDemo mode - no API usage to report.")
            return
        
        try:
            usage_report = self.discussion_manager.get_api_usage_report()
            
            if "error" in usage_report:
                print(f"Usage report not available: {usage_report['error']}")
                return
            
            usage = usage_report["usage_summary"]
            costs = usage_report["cost_estimate"]
            
            print(f"\nAPI Usage Report:")
            print(f"Total Requests: {usage['total_requests']}")
            print(f"Total Failures: {usage['total_failures']}")
            print(f"Daily Cost: ${costs['total_daily_cost']:.4f}")
            print(f"Monthly Est: ${costs['monthly_estimate']:.2f}")
            
            print(f"\nProvider Status:")
            for provider, data in usage["providers"].items():
                status = "✓" if data["available"] else "✗"
                print(f"  {status} {provider}: {data['requests_made']}/{data['daily_limit']} ({data['remaining']} left)")
            
        except Exception as e:
            print(f"Error getting usage report: {e}")
    
    def handle_save_command(self):
        """Handle saving current conversation."""
        if not self.discussion_manager.current_session:
            print("No active discussion to save.")
            return
        
        try:
            result = self.discussion_manager.save_current_conversation()
            if result.get("success"):
                print("✓ Conversation saved successfully!")
                saved_files = result.get("saved_files", {})
                for format_type, filepath in saved_files.items():
                    print(f"  {format_type}: {filepath}")
            else:
                print(f"Failed to save: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"Error saving conversation: {e}")
    
    def handle_list_command(self):
        """Handle listing saved conversations."""
        try:
            conversations = self.discussion_manager.list_saved_conversations()
            if not conversations:
                print("No saved conversations found.")
                return
            
            print(f"\nSaved Conversations ({len(conversations)} total):")
            print("-" * 60)
            for i, conv in enumerate(conversations[:10], 1):  # Show last 10
                created = conv["created_at"][:19] if conv["created_at"] != "Unknown" else "Unknown"
                print(f"{i:2d}. {conv['topic'][:30]:<30} | {created} | {conv['total_messages']} msgs | {conv['rounds']} rounds")
                print(f"    File: {conv['filename']}")
            
            if len(conversations) > 10:
                print(f"\n... and {len(conversations) - 10} more. Use 'search' to find specific conversations.")
        except Exception as e:
            print(f"Error listing conversations: {e}")
    
    def handle_load_command(self, args: List[str]):
        """Handle loading a conversation."""
        if not args:
            print("Please provide a filename. Usage: load <filename>")
            return
        
        filename = args[0]
        try:
            conversation = self.discussion_manager.load_conversation(filename)
            if not conversation:
                print(f"Conversation '{filename}' not found.")
                return
            
            print(f"\nLoaded Conversation: {conversation['topic']}")
            print(f"Date: {conversation['created_at']}")
            print(f"Messages: {len(conversation['messages'])}")
            print(f"Rounds: {conversation['round_number']}")
            
            # Show some messages
            messages = conversation['messages']
            print("\nLast few messages:")
            print("-" * 50)
            for msg in messages[-5:]:  # Show last 5 messages
                timestamp = msg['timestamp'][:19] if len(msg['timestamp']) > 19 else msg['timestamp']
                speaker = msg['speaker']
                content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
                print(f"[{timestamp}] {speaker}: {content}")
                
        except Exception as e:
            print(f"Error loading conversation: {e}")
    
    def handle_search_command(self, args: List[str]):
        """Handle searching conversations."""
        if not args:
            print("Please provide a search query. Usage: search <query>")
            return
        
        query = " ".join(args)
        try:
            results = self.discussion_manager.search_conversations(query)
            if not results:
                print(f"No conversations found matching '{query}'.")
                return
            
            print(f"\nSearch Results for '{query}' ({len(results)} found):")
            print("-" * 60)
            for i, conv in enumerate(results, 1):
                created = conv["created_at"][:19] if conv["created_at"] != "Unknown" else "Unknown"
                print(f"{i}. {conv['topic'][:40]:<40} | {created} | {conv['filename']}")
                
        except Exception as e:
            print(f"Error searching conversations: {e}")
    
    def handle_analyze_command(self, args: List[str]):
        """Handle analyzing a conversation."""
        if not args:
            print("Please provide a filename. Usage: analyze <filename>")
            return
        
        filename = args[0]
        try:
            analysis = self.discussion_manager.get_conversation_analysis(filename)
            if not analysis:
                print(f"Analysis for '{filename}' not found.")
                return
            
            print(f"\nConversation Analysis: {filename}")
            print("=" * 50)
            
            # Agent Performance
            if "agent_performance" in analysis:
                print("\nAgent Performance:")
                for agent, stats in analysis["agent_performance"].items():
                    print(f"  {agent}:")
                    print(f"    Messages: {stats['message_count']}")
                    print(f"    Avg Length: {stats['avg_length']:.0f} chars")
                    print(f"    Participation: {stats['participation_rate']:.1%}")
            
            # Discussion Quality
            if "discussion_quality" in analysis:
                quality = analysis["discussion_quality"]
                print(f"\nDiscussion Quality:")
                print(f"  Message Depth: {quality.get('message_depth', 0):.0f} avg chars")
                print(f"  Interaction Balance: {quality.get('interaction_balance', 0):.1%}")
                print(f"  Topic Coherence: {quality.get('topic_coherence', 0):.1%}")
            
            # Improvements
            if "potential_improvements" in analysis:
                improvements = analysis["potential_improvements"]
                if improvements:
                    print(f"\nSuggested Improvements:")
                    for i, suggestion in enumerate(improvements, 1):
                        print(f"  {i}. {suggestion}")
                        
        except Exception as e:
            print(f"Error analyzing conversation: {e}")
    
    def handle_end_command(self):
        """Handle ending the discussion."""
        if not self.discussion_manager.current_session:
            print("No active discussion to end.")
            return
        
        result = self.discussion_manager.end_discussion()
        
        print(f"\nDiscussion ended successfully!")
        print(f"Topic: {result['topic']}")
        print(f"Total Messages: {result['total_messages']}")
        print(f"Rounds: {result['rounds']}")
        print(f"Summary: {result['summary']}")
        
        # Show saved files
        if "saved_files" in result:
            print(f"\n✓ Conversation saved in multiple formats:")
            for format_type, filepath in result["saved_files"].items():
                print(f"  {format_type}: {filepath}")
        elif "save_error" in result:
            print(f"\n⚠️  Save error: {result['save_error']}")
        
        print(f"\nUse 'list' to see all saved conversations or 'analyze {result.get('saved_files', {}).get('json', '').split('/')[-1]}' to analyze this conversation.")
    
    def handle_help_command(self):
        """Display help information."""
        self.display_welcome()
    
    def run(self):
        """Main CLI loop."""
        self.display_welcome()
        
        while self.running:
            try:
                # Get user input
                user_input = input("\n> ").strip()
                
                if not user_input:
                    continue
                
                # Parse command
                parts = user_input.split()
                command = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                # Handle commands
                if command == "quit" or command == "exit":
                    self.running = False
                    print("Goodbye!")
                
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
                
                elif command == "usage":
                    self.handle_usage_command()
                
                elif command == "save":
                    self.handle_save_command()
                
                elif command == "list":
                    self.handle_list_command()
                
                elif command == "load":
                    self.handle_load_command(args)
                
                elif command == "search":
                    self.handle_search_command(args)
                
                elif command == "analyze":
                    self.handle_analyze_command(args)
                
                elif command == "end":
                    self.handle_end_command()
                
                elif command == "help":
                    self.handle_help_command()
                
                elif command == "messages":
                    if self.discussion_manager.current_session:
                        self.display_messages(self.discussion_manager.current_session.messages)
                    else:
                        print("No active discussion.")
                
                else:
                    print(f"Unknown command: {command}. Type 'help' for available commands.")
            
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit.")
            except Exception as e:
                print(f"Error: {str(e)}")


if __name__ == "__main__":
    cli = SimpleCLI(demo_mode=True)
    cli.run()