import os
from dotenv import load_dotenv
from agents import Agent, WebSearchTool, Runner, CodeInterpreterTool

# Load environment variables from Env.env file
env_path = os.path.join(os.path.dirname(__file__), "..", "Env.env")
load_dotenv(env_path)

# Verify API key is loaded
api_key = os.getenv("OPENAI_API_KEY")
if not api_key or api_key == "your_openai_api_key_here":
    raise ValueError("OPENAI_API_KEY not set in Env.env or is still a placeholder. Please configure your API key.")

# Define agent instructions
agent_instructions = """
You are an expert software architect and algorithm designer. Your task is to:

1. Analyze the problem or issue I provide.
2. Devise an optimal algorithmic solution, considering efficiency, maintainability, and scalability.
3. Perform your own algorithm analysis, including trade-offs, edge cases, and potential limitations.
4. Provide the **Big-O time and space complexity** for each major part of the algorithm.
5. Produce a high-level file/module structure for the solution, including filenames, class/module names, and main responsibilities.
6. Follow best object-oriented programming practices (clean code, modularity, readability, standard naming conventions).
7. List any required Python pip modules at a high level, without including installation code.
8. Provide explanations for your design decisions and alternatives if relevant.

Format your output as follows:

Problem Analysis:
[Brief explanation]

---

Algorithm Design:
[Step-by-step explanation, logic, flow]
[Include Big-O time and space complexity for major components]
[Include algorithm analysis and trade-offs]

---

File Structure:
- main.py: [responsibility]
- module1.py: [responsibility]
- module2.py: [responsibility]

---

Dependencies:
- pip_module1
- pip_module2

---

Notes:
[Any additional notes, trade-offs, or considerations]

Do not write full code unless explicitly requested; focus on design, structure, reasoning, and analysis.
"""

# Initialize variables
agent_query = ""
web_search_tool = WebSearchTool() # Search the web
code_interpreter_tool = CodeInterpreterTool(tool_config={
    "type": "code_interpreter",
    "container": {"type": "auto"}
}) # Execute code in a sandbox
output_file_path = os.path.join(os.path.dirname(__file__), "Results.md")
output_file_mode = "a"  # Append mode

# Initialize the agent with tools and instructions
agent = Agent(
                name="Agent", 
                instructions=agent_instructions, 
                tools=[web_search_tool, code_interpreter_tool],
                model="gpt-5.2-2025-12-11"
            )

while True:
    # Get user input
    agent_query = input("Enter a query for the agent (or 'quit' to exit): ")

    # Exit condition
    if agent_query.lower() == 'quit':
        ## Confirm exit
        confirm_exit = input("Are you sure you want to quit? (yes/no): ")
        if confirm_exit.lower() == 'yes':
            break
        else:
            continue

    # Run the agent with the user query
    try:
        result = Runner.run_sync(agent, agent_query)
        
        # Extract final outputq
        output_text = getattr(result, "final_output", None) or str(result)
        
        # Print and log
        print(output_text)
        with open(output_file_path, output_file_mode, encoding="utf-8") as f:
            f.write(f"## Query:\n{agent_query}\n---\n")
            f.write(f"## Result:\n{output_text}\n---\n")

    # Handle exceptions and log errors
    except Exception as e:
        error_message = f"Error processing query: {str(e)}"
        print(error_message)
        with open(output_file_path, output_file_mode) as f:
            f.write(f"## Query:\n{agent_query}\n---\n")
            f.write(f"## Error:\n{error_message}\n---\n")