from pydantic_ai import Agent, RunContext

from rich.console import Console
import logfire

console = Console()

logfire.configure()
roulette_agent = Agent(
    "openai:gpt-4o-mini",
    deps_type=int,  # where the roulete wheel lands
    result_type=bool,  # whether the customer won
    system_prompt=(
        "Use the `roulette_wheel` function to see if the "
        "customer has won based on the number they provide."
    ),
)


@roulette_agent.tool
async def roulette_wheel(ctx: RunContext[int], square: int) -> str:
    """check if the square is a winner"""
    return True if square == ctx.deps else False


# Run the agent
roulette_wheel_lands_on = 18
print("=======================\n\n")
# result = roulette_agent.run_sync(
#     "Put my money on square eighteen", deps=roulette_wheel_lands_on
# )
result = roulette_agent.run_sync("all on 18", deps=roulette_wheel_lands_on)

console.print(f"\n[cyan]{result.data}[/cyan]\n")
# > True

result = roulette_agent.run_sync(
    "I bet five is the winner", deps=roulette_wheel_lands_on
)
console.print(f"\n[dark_orange]{result.data}[/dark_orange]\n")
# > False
