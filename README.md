# Multi-Agent Discussion LLM System

A collaborative AI research platform where multiple AI agents with different perspectives engage in structured discussions with human participants.

## Features

- **4 Specialized AI Agents**: Skeptic, Synthesizer, Analyst, and Explorer
- **Human-AI Collaboration**: Real-time interaction and moderation
- **Cost-Optimized**: Uses efficient model selection and token management
- **Extensible**: Built with AutoGen framework for easy customization

## Quick Start

### Option 1: Demo Mode (No Setup Required)
Try the system immediately without any dependencies or API keys:

```bash
python3 src/main.py --demo
```

### Option 2: Full Setup with Your API Strategy

Your optimal multi-provider strategy is already configured! 

1. **Automated Setup**
   ```bash
   ./setup_environment.sh
   ```

2. **Manual Setup** (alternative)
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Your .env file is already configured with API keys!
   ```

3. **Run with Real APIs**
   ```bash
   source venv/bin/activate
   python3 src/main.py
   ```

4. **Test Your Multi-Provider Setup**
   ```bash
   source venv/bin/activate
   python3 test_multi_provider.py
   ```

## Project Structure

```
LLM-GD/
├── src/
│   ├── agents/          # Agent implementations
│   ├── core/            # Core discussion logic
│   ├── ui/              # User interfaces
│   └── utils/           # Utilities and helpers
├── config/              # Configuration files
├── tests/               # Test cases
└── docs/                # Documentation
```

## Usage Commands

Once running, use these commands in the CLI:

- `start <topic>` - Start a new discussion
- `speak <message>` - Add your message to the discussion  
- `next` - Let agents respond
- `status` - Show discussion status
- `usage` - Show API usage and costs
- `summary` - Get discussion summary
- `messages` - Show recent messages
- `save` - Save current conversation
- `list` - List saved conversations
- `load <filename>` - Load a conversation
- `search <query>` - Search saved conversations
- `analyze <filename>` - Analyze conversation quality
- `end` - End current discussion
- `help` - Show help
- `quit` - Exit the system

## Development Roadmap

- [x] Phase 1: MVP Implementation
  - [x] Basic multi-agent setup
  - [x] 4 specialized agent personas
  - [x] CLI interface
  - [x] Demo mode
  - [x] Session management
  - [x] **Conversation persistence & analysis**
  - [x] **Multiple export formats (JSON, Markdown, CSV)**
  - [x] **Quality metrics & improvement suggestions**
  - [x] **Search & filtering capabilities**
- [ ] Phase 2: Enhanced Features
  - [ ] Web interface
  - [ ] Real-time fact-checking
  - [ ] Advanced NLP analysis
- [ ] Phase 3: Advanced Capabilities
  - [ ] RAG integration
  - [ ] Advanced analytics
  - [ ] Multi-model support

## Your Cost-Optimized API Strategy

**Configured Providers:**
- ✅ **Google AI Studio**: 5 accounts × 1,500 requests = **7,500 daily requests**
- ⚠️  **Other providers temporarily disabled** (API/pricing changes)

**Total Capacity**: 7,500 requests/day for **$0/month**

**Intelligent Routing (Google-Only):**
- Skeptic Agent → Google AI Studio (Gemini 1.5 Flash)
- Synthesizer Agent → Google AI Studio (Gemini 1.5 Pro)
- Analyst Agent → Google AI Studio (Gemini 1.5 Pro)  
- Explorer Agent → Google AI Studio (Gemini 1.5 Flash)

**Automatic Features:**
- Account rotation across Google accounts
- Quota tracking and fallback
- Real-time usage monitoring
- Graceful degradation to demo mode

## Cost Comparison

- **Your Google Strategy**: $0/month (7,500 requests/day)
- **OpenAI GPT-4**: $120-250/month (same usage)
- **Claude API**: $80-180/month (same usage)
- **Annual Savings**: $960-$2,160