#!/usr/bin/env python3
"""Main entry point for the Multi-Agent Discussion LLM System."""

import sys
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Will handle missing dependencies in check_dependencies()

# Add src to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies(demo_mode=False, use_simple_cli=False):
    """Check if required dependencies are available."""
    missing_deps = []
    
    # OpenAI is only required for non-demo mode
    if not demo_mode:
        try:
            import openai
        except ImportError:
            missing_deps.append("openai (for AI responses)")
    
    # UI dependencies are optional if using simple CLI
    if not use_simple_cli:
        try:
            from colorama import init
            from rich.console import Console
        except ImportError:
            missing_deps.append("colorama and/or rich (for enhanced UI)")
    
    if missing_deps:
        if use_simple_cli and "colorama" in " ".join(missing_deps):
            print("Note: Using simple CLI interface (rich UI not available)")
            return True
        
        print("Error: Missing required dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nPlease install dependencies with: pip install -r requirements.txt")
        
        return False
    
    return True

def check_api_key():
    """Check if OpenAI API key is configured."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY not found in environment variables.")
        print("Please set your API key in the .env file or as an environment variable.")
        print("The system will run in demo mode without actual AI responses.")
        return False
    return True

def main():
    """Main application entry point."""
    print("Starting Multi-Agent Discussion LLM System...")
    
    # Check for demo mode argument
    demo_mode = "--demo" in sys.argv or "-d" in sys.argv
    
    # Determine which CLI to use
    use_simple_cli = False
    try:
        from ui.cli_interface import CLIInterface
        cli_class = CLIInterface
    except ImportError:
        from ui.simple_cli import SimpleCLI
        cli_class = SimpleCLI
        use_simple_cli = True
    
    # Check dependencies
    if not check_dependencies(demo_mode, use_simple_cli):
        sys.exit(1)
    
    # Check API configuration
    has_api_key = check_api_key()
    
    # Force demo mode if no API key
    if not has_api_key and not demo_mode:
        print("No API key found. Running in demo mode - agent responses will be simulated.")
        demo_mode = True
    
    # Import and run the CLI interface
    try:
        if use_simple_cli:
            print("Using simple CLI (enhanced UI not available)")
        
        if demo_mode:
            print("Running in DEMO MODE - agent responses will be simulated.")
        
        cli = cli_class(demo_mode=demo_mode)
        cli.run()
        
    except ImportError as e:
        print(f"Error importing CLI interface: {e}")
        print("Please ensure all modules are properly installed.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutdown requested by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()