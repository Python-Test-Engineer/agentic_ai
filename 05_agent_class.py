import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
import requests
from rich.console import Console

console = Console()

# Load environment variables in a file called .env
# Print the key prefixes to help with any debugging

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
# google_api_key = os.getenv('GOOGLE_API_KEY')

if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set")

if anthropic_api_key:
    print(f"Anthropic API Key exists and begins {anthropic_api_key[:7]}")
else:
    print("Anthropic API Key not set")


openai = OpenAI()
claude = anthropic.Anthropic()


# original propmt
system_message = """
You are an assistant that is very good at determining what tool to use to solve queries.
"""

ai_programming = """

TOOLS

You have two tools:

1. A calculator tool that can perform basic arithmetic operations, such as addition, subtraction, multiplication, and division. If this tool is used then respond as detailed in JSON Format with "next": "do_calculation"
2. A jokes tool that can provide a light-hearted joke for the audience reqested. If this tool is used then respond in JSON Format with "next": "do_joke" and "audience": "audience requested"


OUTPUT

For a user query, determine the best tool. If none of the tools are appropriate, respond with "None".

EXAMPLES

    ## First Example
    
    ### Question
    "What is 5 plus 5?
    ### Response    
    {"tool": "calculator", "next": "do_calculation", "arguments": {"num1": 5, "num2": 5, "operation": "addition"}}

    ## Second Example
    
    ### Question
    "Tell me a joke when I am doing stand up at a Builders Conference"
    ### Response 
    
    {"tool": "joke", "next": "do_joke", "audience": "Pythonistas" }}
    
Thank you for your help.
"""

system_message += ai_programming


user_prompt = "What is 20 divided by 2?"
# user_prompt = "Tell me a joke when I am doing stand up at a Builders Conference"

prompts = [
    {"role": "system", "content": system_message},
    {"role": "user", "content": user_prompt},
]


class Agent:
    def __init__(self, model="gpt-3.5-turbo", prompts=prompts):
        self.model = model
        self.prompt = prompts

    def get_tool(self):
        # print(self.prompt)
        response = openai.chat.completions.create(
            model=self.model, messages=self.prompt
        )
        output = response.choices[0].message.content.replace("\n", "")
        # print(output)
        json_output = output.strip()
        json_output = json.loads(json_output)
        # print(json_output)
        return json_output

    def do_calculation(self, num1, num2, operation):
        if operation == "addition":
            return num1 + num2
        elif operation == "subtraction":
            return num1 - num2
        elif operation == "multiplication":
            return num1 * num2
        elif operation == "division":
            return num1 / num2

    def do_joke(self):

        get_random_joke_internet = requests.get(
            "https://official-joke-api.appspot.com/random_joke"
        )
        return get_random_joke_internet.json()

    def give_answer(self):
        output = self.get_tool()
        print(type(output), output)

        if output["next"] == "do_calculation":
            num1 = output["arguments"]["num1"]
            num2 = output["arguments"]["num2"]
            operation = output["arguments"]["operation"]
            answer = self.do_calculation(num1, num2, operation)
            return answer
        elif output["next"] == "do_joke":
            answer = self.do_joke()
            # answer = "get a joke"
            answer = answer["setup"] + "\n" + answer["punchline"]
            return answer


agent = Agent()
output = agent.get_tool()
# print(output)


answer = agent.give_answer()
answer_text = f"[dark_orange]Answer for '{user_prompt}':[/] [green]{answer}[/]"
console.print(answer_text)
