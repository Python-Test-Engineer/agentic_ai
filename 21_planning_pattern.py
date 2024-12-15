import os
import re
import math
import json
from time import sleep
from dotenv import load_dotenv

from groq import Groq
from openai import OpenAI

from tool_pattern.tool import tool
from utils.extraction import extract_tag_content

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")


if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set")

if anthropic_api_key:
    print(f"Anthropic API Key exists and begins {anthropic_api_key[:7]}")
else:
    print("Anthropic API Key not set")

if groq_api_key:
    print(f"groq API Key exists and begins {groq_api_key[:7]}")
else:
    print("Groq API Key not set")


LLM = "OPENAI"

if LLM == "OPENAI":
    client = OpenAI()
    MODEL = "gpt-4o-mini"
else:
    client = Groq()
    MODEL = "llama-3.1-70b-versatile"


@tool
def sum_two_elements(a: int, b: int) -> int:
    """
    Computes the sum of two integers.

    Args:
        a (int): The first integer to be summed.
        b (int): The second integer to be summed.

    Returns:
        int: The sum of `a` and `b`.
    """
    return a + b


@tool
def multiply_two_elements(a: int, b: int) -> int:
    """
    Multiplies two integers.

    Args:
        a (int): The first integer to multiply.
        b (int): The second integer to multiply.

    Returns:
        int: The product of `a` and `b`.
    """
    return a * b


@tool
def compute_log(x: int) -> float | str:
    """
    Computes the logarithm of an integer `x` with an optional base.

    Args:
        x (int): The integer value for which the logarithm is computed. Must be greater than 0.

    Returns:
        float: The logarithm of `x` to the specified `base`.
    """
    if x <= 0:
        return "Logarithm is undefined for values less than or equal to 0."

    return math.log(x)


@tool
def divide_two_numbers(x: int, y: int) -> float | str:
    """
    A function to divide two numbers.

    Divides `x` by  `y` and returns the result.

    Args:
        x (int): The integer value for which the half value is computed. Must be greater than 0.
        y (int): The integer value for which the half value is computed. Must be greater than 0.

    Returns:
        float: the result of `x` divided by `y`.

    if x <= 0 or y <= 0:

    Args:
         x (int): The integer value x
         y (int): The integer value y

    Returns:
         float: `x` divided by `y`.
    """
    if x <= 0:
        return "Error is undefined for values less than or equal to 0."

    return x / 2


available_tools = {
    "sum_two_elements": sum_two_elements,
    "multiply_two_elements": multiply_two_elements,
    "compute_log": compute_log,
    "divide_two_numbers": divide_two_numbers,
}


# Define the System Prompt as a constant
REACT_SYSTEM_PROMPT = """
You are a function calling AI model. You operate by running a loop with the following steps: Thought, Action, Observation.
You are provided with function signatures within <tools></tools> XML tags.
You may call one or more functions to assist with the user query. Don' make assumptions about what values to plug
into functions. Pay special attention to the properties 'types'. You should use those types as in a Python dict.

For each function call return a json object with function name and arguments within <tool_call></tool_call> XML tags as follows:

<tool_call>
{"name": <function-name>,"arguments": <args-dict>, "id": <monotonically-increasing-id>}
</tool_call>

Here are the available tools / actions:

<tools> 
%s
</tools>

Example session:

<question>What's the current temperature in Madrid?</question>
<thought>I need to get the current weather in Madrid</thought>
<tool_call>{"name": "get_current_weather","arguments": {"location": "Madrid", "unit": "celsius"}, "id": 0}</tool_call>

You will be called again with this:

<observation>{0: {"temperature": 25, "unit": "celsius"}}</observation>

You then output:

<response>The current temperature in Madrid is 25 degrees Celsius</response>

Additional constraints:

- If the user asks you something unrelated to any of the tools above, answer freely enclosing your answer with <response></response> tags.
"""


# print("Tool name: ", sum_two_elements.name)
# print("Tool signature: ", sum_two_elements.fn_signature)


tools_signature = (
    sum_two_elements.fn_signature
    + ",\n"
    + multiply_two_elements.fn_signature
    + ",\n"
    + compute_log.fn_signature
    + ",\n"
    + divide_two_numbers.fn_signature
)


print(tools_signature)

REACT_SYSTEM_PROMPT = REACT_SYSTEM_PROMPT % tools_signature


from planning_pattern.react_agent import ReactAgent


agent = ReactAgent(
    client=client, tools=[sum_two_elements, multiply_two_elements, compute_log]
)

USER_QUESTION = "I want to calculate the sum of 100 and 900 and multiply the result by 10.Then get log of that number"

agent.run(user_msg=USER_QUESTION)
