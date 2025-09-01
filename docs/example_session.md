# Example Discussion Session

This document shows an example session using the Multi-Agent Discussion System in demo mode.

## Starting the System

```bash
$ python3 src/main.py --demo
Starting Multi-Agent Discussion LLM System...
Warning: OPENAI_API_KEY not found in environment variables.
Using simple CLI (enhanced UI not available)
Running in DEMO MODE - agent responses will be simulated.

============================================================
    Multi-Agent Discussion System
    [DEMO MODE] Collaborative AI Research Platform
============================================================

Available Commands:
  start <topic>     - Start a new discussion
  speak <message>   - Add your message to the discussion
  next              - Let agents respond
  status            - Show discussion status
  summary           - Get discussion summary
  messages          - Show recent messages
  end               - End current discussion
  help              - Show this help
  quit              - Exit the system
```

## Example Discussion: "The Future of Remote Work"

### Starting the Discussion

```
> start The future of remote work

Discussion started!
Topic: The future of remote work
Session ID: session_1753557890

Discussion Agents:
  Dr. Skeptic       - Critical Analyst - Questions assumptions
  Dr. Synthesis     - Integrative Thinker - Connects ideas
  Dr. Data          - Evidence Researcher - Provides facts
  Dr. Discovery     - Creative Visionary - Novel perspectives

Type 'next' to let agents start the discussion, or 'speak <message>' to contribute.
```

### Human Contribution

```
> speak I think remote work will become the dominant mode of employment

Your message added to the discussion.
```

### Agent Responses - Round 1

```
> next
Agents are thinking...

2 agent(s) responded:
[10:45:23] Dr. Skeptic: [SKEPTIC] I question the assumptions underlying The future of remote work. What evidence supports this position?
[10:45:25] Dr. Data: [ANALYST] The data on The future of remote work shows significant trends that we should consider.
```

### Another Human Input

```
> speak What about productivity concerns?

Your message added to the discussion.
```

### Agent Responses - Round 2

```
> next
Agents are thinking...

2 agent(s) responded:
[10:46:12] Dr. Synthesis: [SYNTHESIZER] I see interesting connections between the points raised about The future of remote work.
[10:46:14] Dr. Discovery: [EXPLORER] What if we approached The future of remote work from a completely different angle?
```

### Checking Status

```
> status

Discussion Status:
  Status: active
  Topic: The future of remote work
  Round: 2
  Total Messages: 7
  Human Participants: Human

Agent Participation:
  skeptic: 1 messages
  synthesizer: 1 messages
  analyst: 1 messages
  explorer: 1 messages
```

### Viewing Messages

```
> messages

Recent Discussion:
--------------------------------------------------
[10:44:58] SYSTEM: Discussion started on topic: The future of remote work
[10:45:15] Human: I think remote work will become the dominant mode of employment
[10:45:23] Dr. Skeptic: [SKEPTIC] I question the assumptions underlying The future of remote work. What evidence supports this position?
[10:45:25] Dr. Data: [ANALYST] The data on The future of remote work shows significant trends that we should consider.
[10:46:05] Human: What about productivity concerns?
[10:46:12] Dr. Synthesis: [SYNTHESIZER] I see interesting connections between the points raised about The future of remote work.
[10:46:14] Dr. Discovery: [EXPLORER] What if we approached The future of remote work from a completely different angle?
--------------------------------------------------
```

### Ending the Discussion

```
> end

Discussion ended successfully!
Topic: The future of remote work
Total Messages: 7
Rounds: 2
Summary: Discussion on 'The future of remote work' with 4 agent contributions and 2 human contributions across 2 rounds.

> quit
Goodbye!
```

## Key Features Demonstrated

1. **Easy Topic Initiation**: Simple `start <topic>` command
2. **Human-AI Interaction**: Seamless `speak` command for human input
3. **Balanced Agent Participation**: System automatically selects different agents
4. **Role-Based Responses**: Each agent maintains their distinct personality
5. **Session Management**: Complete tracking of discussion state
6. **Multiple Views**: Status, messages, and summary commands
7. **Demo Mode**: Works without any API keys or external dependencies

## Agent Personalities

- **Dr. Skeptic**: Questions assumptions and challenges ideas
- **Dr. Synthesis**: Builds connections between different viewpoints  
- **Dr. Data**: Provides evidence-based perspectives
- **Dr. Discovery**: Offers creative and unconventional approaches

## Next Steps

- Set up with real API keys for actual AI responses
- Try different discussion topics
- Explore longer multi-round discussions
- Use the system for research and brainstorming