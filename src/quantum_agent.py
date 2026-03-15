import os
import json
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from src.quantum_tools import run_deutsch, run_grover, run_simon, run_teleportation


TOOL_MAP = {
    "run_deutsch": run_deutsch,
    "run_grover": run_grover,
    "run_simon": run_simon,
    "run_teleportation": run_teleportation,
}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "run_deutsch",
            "description": "Run Deutsch's algorithm to determine if an oracle is constant or balanced in a single query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "oracle_type": {
                        "type": "string",
                        "enum": ["constant_0", "constant_1", "balanced_identity", "balanced_not"],
                        "description": "constant_0: f(x)=0, constant_1: f(x)=1, balanced_identity: f(x)=x, balanced_not: f(x)=NOT x",
                    }
                },
                "required": ["oracle_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_grover",
            "description": "Run Grover's search algorithm on 2 qubits to find a marked state with ~100% probability.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_state": {
                        "type": "string",
                        "enum": ["00", "01", "10", "11"],
                        "description": "The 2-qubit state to search for.",
                    }
                },
                "required": ["target_state"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_simon",
            "description": "Run Simon's algorithm to find the hidden period string b of a 2-to-1 function.",
            "parameters": {
                "type": "object",
                "properties": {
                    "secret_string": {
                        "type": "string",
                        "description": "Binary secret string, e.g. '11', '101', '110'.",
                    }
                },
                "required": ["secret_string"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_teleportation",
            "description": "Run quantum teleportation to transfer a qubit state from Alice to Bob.",
            "parameters": {
                "type": "object",
                "properties": {
                    "theta_over_pi": {
                        "type": "number",
                        "description": "Angle θ as a fraction of π. E.g. 0.333 → θ=π/3, 0.5 → θ=π/2.",
                    }
                },
                "required": ["theta_over_pi"],
            },
        },
    },
]

SYSTEM_PROMPT = """You are a quantum computing assistant that runs real quantum circuit \
simulations using Qiskit on a local AerSimulator.

Available experiments:
- run_deutsch: Deutsch's algorithm (determines if oracle is constant or balanced in 1 query)
- run_grover: Grover's 2-qubit search (finds marked state with ~100% probability)
- run_simon: Simon's algorithm (finds hidden period string b)
- run_teleportation: Quantum teleportation (transfers qubit state using Bell pair)

When asked to run an experiment, call the tool, then explain:
1. What the algorithm does and why it's quantum-advantageous
2. The measurement results and whether they match theory
Keep responses concise. Pick sensible defaults if parameters aren't specified."""


def run_agent(user_input: str, history: list, api_key: str = "") -> tuple[str, list]:
    """
    Run one turn of the agent.
    history: list of {role, content} dicts (prior turns only).
    api_key: OpenAI key — uses env var if not provided.
    Returns (response_text, tool_results) where tool_results is a list of
    parsed JSON dicts from any tools that were called.
    """
    openai_client = OpenAI(api_key=api_key) if api_key else OpenAI()
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_input})

    tool_results = []

    # Agentic loop: keep going until no more tool calls
    while True:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto",
        )
        msg = response.choices[0].message

        # No tool calls — we have the final answer
        if not msg.tool_calls:
            return msg.content, tool_results

        # Append assistant message with tool calls
        messages.append(msg)

        # Execute each tool call
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            result_str = TOOL_MAP[tc.function.name](**args)

            # Collect parsed results (images etc.) for the UI
            try:
                parsed = json.loads(result_str)
                if "circuit_img" in parsed:
                    tool_results.append(parsed)
            except (json.JSONDecodeError, KeyError):
                pass

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result_str,
            })
