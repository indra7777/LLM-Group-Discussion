# LLM Group Discussion - Web Interface

A beautiful web interface for your multi-agent AI discussion system, designed with the "Creative Co-Pilot" philosophy.

## 🎭 The Three-Act Experience

### Act 1: The Spark ✨
- **Clean, inspiring input screen** that kills writer's block
- **Dynamic placeholder examples** that cycle through creative ideas
- **Goal selection** (Find Unique Angle, Create Script Outline, Stress-Test Ideas)
- **Real-time connection status** with the AI team

### Act 2: The Roundtable 🎪
- **Live chat interface** where you watch AI agents brainstorm in real-time
- **Distinct AI personas** with unique colors and personalities:
  - 📊 **Dr. Data** (Blue) - Evidence-based researcher with hard facts
  - 💡 **Dr. Synthesis** (Green) - Integrative thinker who connects ideas  
  - ❓ **Dr. Skeptic** (Red) - Critical analyst who challenges assumptions
  - 🔮 **Dr. Discovery** (Purple) - Creative visionary with novel perspectives
- **Typing indicators** and smooth animations for that "fly on the wall" feeling
- **Interactive participation** - add your thoughts anytime during the discussion

### Act 3: The Briefing 📋  
- **Organized, actionable output** that's ready to use
- **Executive summary** with the core thesis prominently displayed
- **Tabbed sections** for different content types:
  - **Overview** - Discussion stats and quick actions
  - **Script Outline** - Main narrative flow ready for production
  - **Key Facts** - Data points and sources for research
  - **Creative Angles** - Novel perspectives and fresh takes
  - **Q&A Prep** - Counterarguments and title suggestions
- **One-click copy buttons** for each section
- **Export functionality** to Markdown files

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ with your existing LLM-GD environment
- Node.js 16+ and npm
- OpenAI API key (set in `.env` file)

### One-Command Start
```bash
python start_web.py
```

This will:
1. Check all dependencies
2. Install frontend packages if needed
3. Start the FastAPI backend (port 8000)
4. Start the React frontend (port 3000)
5. Open your browser to the beautiful interface

### Manual Start (Alternative)

**Backend:**
```bash
pip install fastapi uvicorn websockets
python web_api.py
```

**Frontend:**
```bash
cd web
npm install
npm start
```

## 🛠 Technical Architecture

### Backend (FastAPI)
- **RESTful API** with endpoints for discussion management
- **WebSocket support** for real-time message streaming
- **Integration** with existing `DiscussionManager` and agent system
- **Research tool integration** for web search capabilities

### Frontend (React)
- **Modern React** with hooks and functional components
- **Framer Motion** for smooth, professional animations
- **Lucide React** icons for consistent visual language
- **React Hot Toast** for elegant notifications
- **Responsive design** that works on desktop and mobile

### Real-time Communication
- **WebSocket connection** for live updates during discussions
- **Automatic reconnection** if connection is lost
- **Typing indicators** and loading states for smooth UX
- **Toast notifications** for system feedback

## 🎨 Design Philosophy

The interface follows the "Creative Co-Pilot" philosophy:

- **Inspirational** - Kills writer's block with dynamic prompts and smooth animations
- **Effortless** - Smooth flow from vague idea to structured content
- **Engaging** - Feels like watching a live brainstorming session
- **Actionable** - Output is immediately useful and easy to export

## 📁 File Structure

```
web/
├── public/
│   └── index.html          # Beautiful loading screen
├── src/
│   ├── components/
│   │   ├── SparkScreen.js      # Act 1: Input screen
│   │   ├── RoundtableScreen.js # Act 2: Live discussion
│   │   └── BriefingScreen.js   # Act 3: Structured output
│   ├── App.js              # Main app with screen transitions
│   ├── App.css             # Global styles and utilities
│   └── index.js            # React entry point
├── package.json            # Frontend dependencies
web_api.py                  # FastAPI backend server
start_web.py                # One-command startup script
```

## 🎯 Features

### User Experience
- **Smooth screen transitions** with Framer Motion
- **Real-time WebSocket** updates during discussions
- **Copy to clipboard** for all content sections
- **Export to Markdown** for further editing
- **Responsive design** for all screen sizes
- **Connection status** indicators
- **Loading states** and progress feedback

### Content Creation
- **Dynamic title generation** based on discussion content
- **Structured script outlines** ready for production
- **Key facts extraction** with source attribution
- **Counterargument preparation** for robust content
- **Creative angle suggestions** for unique perspectives

### Technical Features
- **Hot reload** during development
- **Error handling** with user-friendly messages
- **Graceful fallbacks** when APIs are unavailable
- **Performance optimized** with lazy loading
- **SEO friendly** with proper meta tags

## 🔧 Customization

### Adding New Agent Personas
Edit `RoundtableScreen.js` to modify the `agentPersonas` object with new colors, emojis, and descriptions.

### Styling Changes
The design system is in `App.css` with utility classes for rapid customization of colors, spacing, and animations.

### New Export Formats
Extend `BriefingScreen.js` to add new export formats (PDF, DOCX, etc.) by modifying the `handleExportAll` function.

## 🐛 Troubleshooting

**Frontend won't start:**
- Ensure Node.js 16+ is installed
- Try `rm -rf web/node_modules && npm install`

**Backend API errors:**
- Check that your `.env` file has valid API keys
- Verify the existing CLI version works first

**WebSocket connection issues:**
- Check firewall settings for ports 3000 and 8000
- Ensure no other services are using these ports

## 🎉 What's Next?

This web interface transforms your CLI tool into a professional, engaging platform for content creators. The three-act structure guides users from inspiration to actionable output, making AI brainstorming feel natural and exciting.

Ready to turn ideas into compelling content? Start the web interface and let your creative co-pilot take flight! ✨