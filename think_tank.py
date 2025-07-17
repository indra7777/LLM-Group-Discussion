import argparse
import os
import sys
from duckduckgo_search import DDGS
import google.generativeai as genai

# --- CONFIGURATION ---

# Configure the Gemini API
try:
    # For this version, we'll stick to Gemini, but the new structure allows for easy expansion.
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    MODEL = genai.GenerativeModel('gemini-1.5-flash')
except KeyError:
    print("Error: GEMINI_API_KEY environment variable not set.")
    sys.exit(1)

# --- CLASSES ---

class Agent:
    """Represents an AI agent with a specific persona and research capabilities."""
    def __init__(self, name, persona):
        self.name = name
        self.persona = persona

    def _generate_content(self, prompt):
        """Generates content using the configured LLM."""
        try:
            # In a multi-LLM setup, this method would be an abstraction layer.
            response = MODEL.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating content for {self.name}: {e}")
            return "[An error occurred during content generation]"

    def generate_search_query(self, topic, history):
        """Generates a targeted search query based on the discussion."""
        print(f"\n--- {self.name} is generating a search query... ---")
        prompt = (
            f"{self.persona}\n\n"
            f"The main topic is: '{topic}'.\n"
            f"The conversation so far:\n{''.join(history)}\n"
            f"Based on this, what is a short, specific search query to find new information for your next point? "
            f"Respond with ONLY the search query."
        )
        query = self._generate_content(prompt).strip().replace('"', '')
        print(f"Query: '{query}'")
        return query

    def research(self, query):
        """Performs a web search and returns a formatted summary."""
        print(f"--- {self.name} is researching '{query}'... ---")
        try:
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(query, max_results=3)]
                if not results:
                    return "No search results found."
                summary = "\n".join([f"- {res['title']}: {res['body']}" for res in results])
                print("--- Research Summary ---")
                print(summary)
                print("------------------------")
                return summary
        except Exception as e:
            print(f"Error during web search for {self.name}: {e}")
            return "There was an error performing the web search."

    def respond(self, topic, history, research_summary):
        """Generates a response based on persona, history, and research."""
        print(f"--- {self.name} is formulating a response... ---")
        prompt = (
            f"{self.persona}\n\n"
            f"The main topic is: '{topic}'.\n"
            f"The conversation so far:\n{''.join(history)}\n"
            f"**Your research results:**\n{research_summary}\n\n"
            f"Your turn, {self.name}. Based **only** on the provided research and the discussion, what are your thoughts? "
            f"Cite the source title in your response (e.g., 'According to [Source Title]...')."
        )
        response = self._generate_content(prompt)
        print(f"\n--- {self.name}'s Response ---")
        print(response)
        print("--------------------------")
        return response

class Discussion:
    """Manages the multi-agent discussion workflow."""
    def __init__(self, topic, agents, rounds=2):
        self.topic = topic
        self.agents = agents
        self.rounds = rounds
        self.history = []
        self.transcript = f"# Discussion on: {self.topic}\n\n"

    def run(self):
        """Executes the discussion for the specified number of rounds."""
        print(f"--- Starting discussion on: {self.topic} ---")
        for i in range(self.rounds):
            print(f"\n================ ROUND {i+1} ================")
            for agent in self.agents:
                # Agent's turn
                search_query = agent.generate_search_query(self.topic, self.history)
                if "[An error occurred" in search_query: continue

                research_summary = agent.research(search_query)
                response = agent.respond(self.topic, self.history, research_summary)

                # Record everything
                self.history.append(f"**{agent.name}:** {response}\n")
                self.transcript += f"**{agent.name} searched for:** `{search_query}`\n\n"
                self.transcript += f"**Research Results:**\n{research_summary}\n\n"
                self.transcript += f"**{agent.name}:** {response}\n\n"
        
        self.save_transcript()

    def save_transcript(self):
        """Saves the discussion transcript to a Markdown file."""
        filename = f"{self.topic.replace(' ', '_').replace('/', '_')}.md"
        with open(filename, "w") as f:
            f.write(self.transcript)
        print(f"\nTranscript saved to {filename}")

# --- MAIN EXECUTION ---

def main():
    """Initializes agents and runs the discussion."""
    parser = argparse.ArgumentParser(description="AI Discussion Panel")
    parser.add_argument("topic", type=str, help="The topic for the AI discussion.")
    args = parser.parse_args()

    personas = {
        "Analyst": "You are an analyst. Focus on data, facts, and neutral analysis.",
        "Skeptic": "You are a skeptic. Challenge assumptions and point out potential flaws.",
        "Visionary": "You are a visionary. Explore future implications and creative ideas.",
        "Ethicist": "You are an ethicist. Discuss the moral and ethical dimensions.",
    }

    agents = [Agent(name, persona) for name, persona in personas.items()]
    
    discussion = Discussion(topic=args.topic, agents=agents)
    discussion.run()

if __name__ == "__main__":
    main()
