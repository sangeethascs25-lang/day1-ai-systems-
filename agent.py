"""System 3: AI agent. LLM + tools + loop."""

import json

from config import client, MODEL, QUESTIONS, banner
from tools import TOOLS, TOOL_FUNCTIONS


SYSTEM_PROMPT = (
    "You are a college fee assistant. "
    "Never guess a fee. Always use get_course_fee for course fees. "
    "Use calculator for percentage calculations and other arithmetic when needed. "
    "Available course codes: CS101, AI202, DS303. "
    "If you have already obtained two course fees and need only to compare them, "
    "you may calculate the difference yourself without using calculator. "
    "If no tool is needed, answer directly."
)


def agent(question, max_steps=6, verbose=True):

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]

    for step in range(1, max_steps + 1):

        # Ask LLM what to do
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            temperature=0
        )

        message = response.choices[0].message

        # If no tool is requested, final answer
        if not message.tool_calls:
            return message.content.strip()

        # Add assistant message
        messages.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments
                    }
                }
                for call in message.tool_calls
            ]
        })

        # Run each tool
        for call in message.tool_calls:

            name = call.function.name
            arguments = call.function.arguments or "{}"

            # Remove accidental provider suffix if present
            if "<|channel|>" in name:
                name = name.split("<|channel|>")[0]

            function = TOOL_FUNCTIONS.get(name)

            if function:
                result = function(**json.loads(arguments))
            else:
                result = f"Unknown tool: {name}"

            if verbose:
                print(
                    f"  step {step}: {name}({arguments}) -> {result}"
                )

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(result)
            })

    return "Stopped: maximum steps reached without a final answer."


if __name__ == "__main__":

    banner("SYSTEM 3: AI AGENT")

    for question in QUESTIONS:
        print("Q:", question)
        print("A:", agent(question))
        print("-" * 70)