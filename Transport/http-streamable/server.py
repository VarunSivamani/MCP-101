import os
import os
from dotenv import load_dotenv
load_dotenv()

import asyncio
import logging

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel(os.getenv("MODEL_NAME"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

async def generate_with_timeout(model, prompt, timeout=10):
    try:
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                lambda: model.generate_content(contents=prompt)
            ),
            timeout=timeout
        )
        return response
    except Exception as e:
        logging.error(e)
        return None


async def main():
    transport = StreamableHttpTransport("http://127.0.0.1:8000/mcp")

    async with Client(transport) as client:
        await client.ping()
        logging.info("Ping successful!")

        # List tools
        tools = await client.list_tools()
        logging.info("Tools available: %s", tools)

        # Build tool description block
        tool_desc = []
        for t in tools:
            name = t.name
            desc = t.description
            props = t.inputSchema["properties"]
            params = ", ".join(f"{p}: {props[p]['type']}" for p in props)
            tool_desc.append(f"- {name}({params}) — {desc}")
        tool_block = "\n".join(tool_desc)

        # Few-shot example
        few_shot_example = """
            ### Example of correct tool use

            User asks:
            "Compute (10 + 5) * (4 - 1)"

            Correct behavior:

            Step 1 → Model figures out addition is needed:
            FUNCTION_CALL: add|10|5

            (Assume tool returns: 15)

            Step 2 → Model figures out subtraction is needed:
            FUNCTION_CALL: subtract|4|1

            (Assume tool returns: 3)

            Step 3 → Model multiplies results USING TOOL:
            FUNCTION_CALL: multiply|15|3

            (Assume tool returns: 45)

            Step 4 → Model outputs final answer:
            FINAL_ANSWER: 45
        """

        system_prompt = f"""
            You are a deterministic tool-using math agent.
            You NEVER compute numbers yourself — you ALWAYS call tools.

            TOOLS AVAILABLE:
            {tool_block}

            Your output must ALWAYS follow this pattern:

            1) When calling a tool:
            FUNCTION_CALL: tool_name|arg1|arg2

            2) When you are done:
            FINAL_ANSWER: [number]

            STRICT RULES:
            - NO natural language.
            - NO code blocks.
            - NO backticks.
            - NO alternative formats.
            - ONLY the single exact line you are asked for.

            {few_shot_example}

            Now solve the new problem BELOW using the same pattern.
        """

        problem = "(23 + 7) * (15 - 8)"
        prompt = f"{system_prompt}\nProblem: {problem}"

        response = await generate_with_timeout(model, prompt)
        if response:
            logging.info("\nMODEL RAW OUTPUT:")
            logging.info(response.text)

asyncio.run(main())
