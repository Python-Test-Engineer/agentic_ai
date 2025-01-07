from pydantic_ai import Agent, RunContext

from rich.console import Console
import logfire

console = Console()

logfire.configure()
roulette_agent = Agent(
    "openai:gpt-4o-mini",
    deps_type=int,
    result_type=bool,
    system_prompt=(
        "Use the `roulette_wheel` function to see if the "
        "customer has won based on the number they provide."
    ),
)


@roulette_agent.tool
async def roulette_wheel(ctx: RunContext[int], square: int) -> str:
    """check if the square is a winner"""
    return "winner" if square == ctx.deps else "loser"


# Run the agent
success_number = 18
print("=======================\n\n")
result = roulette_agent.run_sync("Put my money on square eighteen", deps=success_number)
console.print(f"\n[green]{result.data}[/green]")
# > True

result = roulette_agent.run_sync("I bet five is the winner", deps=success_number)
console.print(f"\n[dark_orange]{result.data}[/dark_orange]\n")
# > False
