"""Conversation storage and analysis system."""

import json
import csv
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import uuid


@dataclass
class ConversationMetrics:
    """Metrics for analyzing conversation quality."""
    total_messages: int = 0
    agent_messages: int = 0
    human_messages: int = 0
    rounds: int = 0
    avg_message_length: float = 0.0
    agent_participation: Dict[str, int] = None
    duration_minutes: float = 0.0
    topic_coverage_score: float = 0.0
    
    def __post_init__(self):
        if self.agent_participation is None:
            self.agent_participation = {}


class ConversationStorage:
    """Handles saving, loading, and analyzing conversations."""
    
    def __init__(self, storage_dir: str = "conversations"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        
        # Create subdirectories
        for subdir in ["json", "markdown", "csv", "analysis"]:
            os.makedirs(os.path.join(storage_dir, subdir), exist_ok=True)
    
    def save_conversation(self, session, format_types: List[str] = None) -> Dict[str, str]:
        """Save conversation in multiple formats."""
        if format_types is None:
            format_types = ["json", "markdown"]
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c for c in session.topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_topic = safe_topic.replace(' ', '_')[:30]
        base_filename = f"{timestamp}_{safe_topic}_{session.session_id}"
        
        saved_files = {}
        
        # Prepare conversation data
        conversation_data = {
            "session_id": session.session_id,
            "topic": session.topic,
            "created_at": session.created_at.isoformat(),
            "round_number": session.round_number,
            "is_active": session.is_active,
            "human_participants": session.human_participants,
            "messages": [
                {
                    "speaker": msg["speaker"],
                    "content": msg["content"],
                    "type": msg["type"],
                    "timestamp": msg["timestamp"].isoformat(),
                    "round": msg["round"]
                }
                for msg in session.messages
            ],
            "metrics": self._calculate_metrics(session)
        }
        
        # Save in requested formats
        if "json" in format_types:
            json_path = os.path.join(self.storage_dir, "json", f"{base_filename}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)
            saved_files["json"] = json_path
        
        if "markdown" in format_types:
            md_path = os.path.join(self.storage_dir, "markdown", f"{base_filename}.md")
            self._save_as_markdown(conversation_data, md_path)
            saved_files["markdown"] = md_path
        
        if "csv" in format_types:
            csv_path = os.path.join(self.storage_dir, "csv", f"{base_filename}.csv")
            self._save_as_csv(conversation_data, csv_path)
            saved_files["csv"] = csv_path
        
        # Save analysis
        analysis_path = os.path.join(self.storage_dir, "analysis", f"{base_filename}_analysis.json")
        analysis = self._analyze_conversation(conversation_data)
        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        saved_files["analysis"] = analysis_path
        
        return saved_files
    
    def _save_as_markdown(self, conversation_data: Dict, filepath: str):
        """Save conversation as markdown file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Discussion: {conversation_data['topic']}\n\n")
            f.write(f"**Session ID:** {conversation_data['session_id']}\n")
            f.write(f"**Date:** {conversation_data['created_at']}\n")
            f.write(f"**Rounds:** {conversation_data['round_number']}\n")
            f.write(f"**Participants:** {', '.join(conversation_data['human_participants'])}\n\n")
            
            # Metrics summary
            metrics = conversation_data['metrics']
            f.write("## Summary\n\n")
            f.write(f"- **Total Messages:** {metrics['total_messages']}\n")
            f.write(f"- **Agent Messages:** {metrics['agent_messages']}\n")
            f.write(f"- **Human Messages:** {metrics['human_messages']}\n")
            f.write(f"- **Duration:** {metrics['duration_minutes']:.1f} minutes\n\n")
            
            # Agent participation
            f.write("## Agent Participation\n\n")
            for agent, count in metrics['agent_participation'].items():
                f.write(f"- **{agent}:** {count} messages\n")
            f.write("\n")
            
            # Conversation
            f.write("## Conversation\n\n")
            current_round = -1
            
            for msg in conversation_data['messages']:
                if msg['round'] != current_round:
                    current_round = msg['round']
                    if current_round > 0:
                        f.write(f"\n### Round {current_round}\n\n")
                
                timestamp = datetime.fromisoformat(msg['timestamp']).strftime("%H:%M:%S")
                
                if msg['type'] == 'system':
                    f.write(f"*{timestamp} - {msg['content']}*\n\n")
                elif msg['type'] == 'human':
                    f.write(f"**{msg['speaker']}** ({timestamp}):\n{msg['content']}\n\n")
                else:  # agent
                    f.write(f"**{msg['speaker']}** ({timestamp}):\n{msg['content']}\n\n")
    
    def _save_as_csv(self, conversation_data: Dict, filepath: str):
        """Save conversation as CSV file."""
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'timestamp', 'round', 'speaker', 'type', 'content', 'message_length'
            ])
            
            # Messages
            for msg in conversation_data['messages']:
                writer.writerow([
                    msg['timestamp'],
                    msg['round'],
                    msg['speaker'],
                    msg['type'],
                    msg['content'],
                    len(msg['content'])
                ])
    
    def _calculate_metrics(self, session) -> Dict[str, Any]:
        """Calculate conversation metrics."""
        if not session.messages:
            return asdict(ConversationMetrics())
        
        agent_messages = [msg for msg in session.messages if msg["type"] == "agent"]
        human_messages = [msg for msg in session.messages if msg["type"] == "human"]
        
        # Agent participation
        agent_participation = {}
        for msg in agent_messages:
            speaker = msg["speaker"]
            agent_participation[speaker] = agent_participation.get(speaker, 0) + 1
        
        # Duration
        start_time = session.created_at
        last_message_time = session.messages[-1]["timestamp"]
        duration_minutes = (last_message_time - start_time).total_seconds() / 60
        
        # Average message length
        all_content_lengths = [len(msg["content"]) for msg in session.messages if msg["type"] != "system"]
        avg_length = sum(all_content_lengths) / len(all_content_lengths) if all_content_lengths else 0
        
        return asdict(ConversationMetrics(
            total_messages=len(session.messages),
            agent_messages=len(agent_messages),
            human_messages=len(human_messages),
            rounds=session.round_number,
            avg_message_length=avg_length,
            agent_participation=agent_participation,
            duration_minutes=duration_minutes,
            topic_coverage_score=self._calculate_topic_coverage(session)
        ))
    
    def _calculate_topic_coverage(self, session) -> float:
        """Calculate how well the conversation covered the topic."""
        # Simple heuristic: more agent participation = better coverage
        agent_messages = [msg for msg in session.messages if msg["type"] == "agent"]
        unique_agents = len(set(msg["speaker"] for msg in agent_messages))
        
        # Score based on agent diversity and message count
        if len(agent_messages) == 0:
            return 0.0
        
        diversity_score = unique_agents / 4.0  # Assuming 4 possible agents
        volume_score = min(len(agent_messages) / 10.0, 1.0)  # Cap at 10 messages
        
        return (diversity_score + volume_score) / 2.0
    
    def _analyze_conversation(self, conversation_data: Dict) -> Dict[str, Any]:
        """Perform detailed conversation analysis."""
        messages = conversation_data['messages']
        agent_messages = [msg for msg in messages if msg['type'] == 'agent']
        
        analysis = {
            "conversation_flow": self._analyze_flow(messages),
            "agent_performance": self._analyze_agent_performance(agent_messages),
            "discussion_quality": self._analyze_quality(messages),
            "potential_improvements": self._suggest_improvements(conversation_data),
            "timestamp": datetime.now().isoformat()
        }
        
        return analysis
    
    def _analyze_flow(self, messages: List[Dict]) -> Dict[str, Any]:
        """Analyze conversation flow patterns."""
        round_distribution = {}
        speaker_transitions = []
        
        for i, msg in enumerate(messages):
            # Round distribution
            round_num = msg['round']
            if round_num not in round_distribution:
                round_distribution[round_num] = []
            round_distribution[round_num].append(msg['speaker'])
            
            # Speaker transitions
            if i > 0 and msg['type'] != 'system':
                prev_speaker = messages[i-1]['speaker']
                current_speaker = msg['speaker']
                speaker_transitions.append(f"{prev_speaker} -> {current_speaker}")
        
        return {
            "round_distribution": round_distribution,
            "speaker_transitions": speaker_transitions,
            "avg_messages_per_round": len([m for m in messages if m['type'] != 'system']) / max(1, len(round_distribution))
        }
    
    def _analyze_agent_performance(self, agent_messages: List[Dict]) -> Dict[str, Any]:
        """Analyze individual agent performance."""
        agent_stats = {}
        
        for msg in agent_messages:
            speaker = msg['speaker']
            if speaker not in agent_stats:
                agent_stats[speaker] = {
                    "message_count": 0,
                    "total_length": 0,
                    "avg_length": 0,
                    "rounds_participated": set()
                }
            
            stats = agent_stats[speaker]
            stats["message_count"] += 1
            stats["total_length"] += len(msg['content'])
            stats["rounds_participated"].add(msg['round'])
        
        # Calculate averages and participation rates
        for speaker, stats in agent_stats.items():
            stats["avg_length"] = stats["total_length"] / stats["message_count"]
            stats["rounds_participated"] = len(stats["rounds_participated"])
            stats["participation_rate"] = stats["rounds_participated"] / max(1, max(msg['round'] for msg in agent_messages))
        
        return agent_stats
    
    def _analyze_quality(self, messages: List[Dict]) -> Dict[str, Any]:
        """Analyze discussion quality indicators."""
        non_system_messages = [msg for msg in messages if msg['type'] != 'system']
        
        # Basic quality metrics
        quality_indicators = {
            "message_depth": sum(len(msg['content']) for msg in non_system_messages) / len(non_system_messages) if non_system_messages else 0,
            "interaction_balance": self._calculate_interaction_balance(messages),
            "topic_coherence": self._calculate_topic_coherence(messages)
        }
        
        return quality_indicators
    
    def _calculate_interaction_balance(self, messages: List[Dict]) -> float:
        """Calculate how balanced the interaction is between agents and humans."""
        agent_count = len([msg for msg in messages if msg['type'] == 'agent'])
        human_count = len([msg for msg in messages if msg['type'] == 'human'])
        
        if agent_count + human_count == 0:
            return 0.0
        
        # Ideal ratio is around 2:1 (agents:humans)
        ideal_ratio = 2.0
        actual_ratio = agent_count / max(1, human_count)
        
        # Score closer to ideal ratio
        balance_score = 1.0 - abs(actual_ratio - ideal_ratio) / (ideal_ratio + 1)
        return max(0.0, balance_score)
    
    def _calculate_topic_coherence(self, messages: List[Dict]) -> float:
        """Simple topic coherence calculation."""
        # This is a placeholder - could be enhanced with NLP
        content_messages = [msg for msg in messages if msg['type'] != 'system']
        if len(content_messages) < 2:
            return 1.0
        
        # Simple heuristic: longer messages generally indicate more thoughtful responses
        avg_length = sum(len(msg['content']) for msg in content_messages) / len(content_messages)
        
        # Normalize to 0-1 scale
        return min(avg_length / 200.0, 1.0)
    
    def _suggest_improvements(self, conversation_data: Dict) -> List[str]:
        """Suggest improvements based on conversation analysis."""
        suggestions = []
        metrics = conversation_data['metrics']
        
        # Check agent participation balance
        participation = metrics['agent_participation']
        if participation:
            max_participation = max(participation.values())
            min_participation = min(participation.values())
            
            if max_participation - min_participation > 2:
                suggestions.append("Consider more balanced agent participation across rounds")
        
        # Check conversation length
        if metrics['total_messages'] < 10:
            suggestions.append("Conversation could benefit from more rounds to develop ideas")
        
        # Check human engagement
        if metrics['human_messages'] < 2:
            suggestions.append("More human interaction could guide the discussion better")
        
        # Check duration
        if metrics['duration_minutes'] < 5:
            suggestions.append("Longer discussions tend to produce more insights")
        
        return suggestions
    
    def list_conversations(self) -> List[Dict[str, Any]]:
        """List all saved conversations with basic info."""
        conversations = []
        json_dir = os.path.join(self.storage_dir, "json")
        
        for filename in os.listdir(json_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(json_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    conversations.append({
                        "filename": filename,
                        "topic": data.get("topic", "Unknown"),
                        "created_at": data.get("created_at", "Unknown"),
                        "total_messages": data.get("metrics", {}).get("total_messages", 0),
                        "rounds": data.get("round_number", 0)
                    })
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
        
        # Sort by creation date, newest first
        conversations.sort(key=lambda x: x["created_at"], reverse=True)
        return conversations
    
    def load_conversation(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load a specific conversation."""
        filepath = os.path.join(self.storage_dir, "json", filename)
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading conversation: {e}")
            return None
    
    def search_conversations(self, query: str) -> List[Dict[str, Any]]:
        """Search conversations by topic or content."""
        query = query.lower()
        matching_conversations = []
        
        for conv in self.list_conversations():
            # Search in topic
            if query in conv["topic"].lower():
                matching_conversations.append(conv)
                continue
            
            # Search in content
            full_conv = self.load_conversation(conv["filename"])
            if full_conv:
                for msg in full_conv.get("messages", []):
                    if query in msg.get("content", "").lower():
                        matching_conversations.append(conv)
                        break
        
        return matching_conversations