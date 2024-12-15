import os
import json
import subprocess
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup

from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()
print(api_key)

# Send the planning system prompt to the LLM to create a plan and save those tasks as a list.
# For every task in that list:
# Keep track of the task given to the agent.
# Pull in the task prompt with the history.
# Call the LLM to choose a tool based on the given task and return as JSON.
# Update our memory with the LLM response.
# Match the tool called by the LLM to one of the tools available.
# Run the function called.
# Start the next task.
class Agent:
    def __init__(self):

        ## Memory
        self.memory_tasks = []
        self.memory_responses = []

        self.planned_actions = []
        self.url = ""
        self.links = []
        self.planning_system_prompt = """
        % Role: 
        You are an AI assistant helping a user plan a task. You have access to % Tools to help you with the order of tasks.

        % Task: 
        Check the user's query and provide a plan for the order of tools to use for the task if appropriate. Do not execute only out line the tasks in order to accomplish the user's query.

        % Instructions: 
        Create a plan for the order of tools to use for the task based on the user's query.
        Choose the approapriate tool or tools to use for the task based on the user's query.
        Tools that require content will have a variable_name and variable_value.
        A tool variable value can be another tool or a variable from a previous tool or the variable that is set in memory.
        If a variable is set in memory, use the variable value from memory.
        If the tool doesn't need variables, put the tool name in the variable_name and leave the variable_value empty.
        Memories will be stored for future use. If the output of a tool is needed, use the variable from memory.

        % Tools:
        open_chrome - Open Google Chrome
        navigate_to_hackernews - Navigate to Hacker News
        get_https_links - Get all HTTPS links from a page requires URL
        
        % Output:
        Plan of how to accomplish the user's query and what tools to use in order
        Each step should be one a single line with the tool to use and the variables if needed
        """

    def update_system_prompt(self):
        self.system_prompt = f"""
            % Role: 
            You are an AI assistant helping a user with a task. You have access to % Tools to help you with the task.

            % Task: 
            Check the user's query and provide a tool or tools to use for the task if appropriate. Always check the memory for previous questions and answers to choose the appropriate tool.

            % Memory:
            You have a memory of the user's questions and your answers.
            Previous Questions: {self.memory_tasks}
            Previous Answers: {self.memory_responses}

            % Instructions: 
            Choose the appropriate tool to use for the task based on the user's query.
            Tools that require content will have a variable_name and variable_value.
            A tool variable value can be another tool or a variable from a previous tool.
            Check the memory for previous questions and answers to choose the appropriate variable if it has been set.
            If the tool doesn't need variables, put the tool name in the variable_name and leave the variable_value empty.

            % Tools:
            open_chrome - Open Google Chrome
            navigate_to_hackernews - Navigate to Hacker News
            get_https_links - Get all HTTPS links from a page requires URL

            % Output:
            json only

            {{
                "tool": "tool" or ""
                "variables": [
                    {{
                        "variable_name": "variable_name" or ""
                        "variable_value": "variable_value" or ""
                    }}
                ]
            }}
            """

    def openai_call(self, query: str, system_prompt: str, json_format: bool = False):

        if json_format:
            format_response = {"type": "json_object"}
        else:
            format_response = {"type": "text"}

        completion = client.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User query: {query}"},
            ],
            response_format=format_response,
        )
        llm_response = completion.choices[0].message.content
        # print(llm_response)
        return llm_response

    def navigate_to_hackernews(self, query):
        self.url = "https://news.ycombinator.com/"
        try:
            # subprocess.run(["open", "-a", "Google Chrome", self.url], check=True)
            print(f"Opened '{query}' opened in Google Chrome.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to open search in Google Chrome: {e}")

    def get_https_links(self, url="https://news.ycombinator.com/"):

        try:
            response = requests.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a")

            for link in links:
                link_text = link.get_text(strip=True)
                link_url = link.get("href")
                if link_url and link_url.startswith("https"):
                    print(f"Link Name: {link_text if link_text else 'No text'}")
                    print(f"Link URL: {link_url}")
                    print("---")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the URL: {e}")

    ## Plan and Execute
    def run(self, prompt: str):
        ## Planning
        planning = self.openai_call(prompt, self.planning_system_prompt)
        self.planned_actions = planning.split("\n")

        ## Task Execution
        for task in self.planned_actions:
            print(f"\n\nExecuting task: {task}")
            self.memory_tasks.append(task)
            self.update_system_prompt()
            task_call = self.openai_call(task, self.system_prompt, True)
            self.memory_responses.append(task_call)

            try:
                task_call_json = json.loads(task_call)
            except json.JSONDecodeError as e:
                print(f"Error decoding task call: {e}")
                continue

            tool = task_call_json.get("tool")

            if tool == "open_chrome":
                print("Opening Google Chrome...")

            elif tool == "get_https_links":
                self.links = self.get_https_links(self.url)
                self.memory_responses.append(
                    f"get_https_links=completed. variable urls = {self.links}"
                )

            elif tool == "navigate_to_hackernews":
                # query = variables[0].get("variable_value", "")
                query = "Get all the links from Hacker News."
                self.navigate_to_hackernews(query)
                self.memory_responses.append(
                    f"navigate_to_hackernews=completed. variable query = {query}"
                )


if __name__ == "__main__":
    agent = Agent()

    while True:
        prompt = input("Please enter a prompt (or type 'exit' to quit): ")

        if prompt.lower() == "exit":
            break
        agent.run(prompt)
