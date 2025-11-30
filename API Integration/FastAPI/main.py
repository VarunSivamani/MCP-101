import os
import logging
import asyncio
import google.generativeai as genai
from fastmcp import FastMCP
from fastmcp.client import Client
from app import app, products_db
from models import Product, ProductResponse
from utils import *

from dotenv import load_dotenv
load_dotenv()

# Enable new OpenAPI parser
os.environ["FASTMCP_EXPERIMENTAL_ENABLE_NEW_OPENAPI_PARSER"] = "true"

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel(os.getenv("MODEL_NAME"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# using FastAPI endpoints as MCP tools
mcp = FastMCP.from_fastapi(app=app)

# creating a simple MCP Tool for demonstration
@mcp.tool
def obtain_product_from_db(product_id: int) -> ProductResponse:
    """Get a product by ID from the DB."""
    return products_db[product_id]


async def demo(prompt):
    async with Client(mcp) as client:
        await client.ping()
        # logging.info("Ping successful!")

        # List tools
        tools = await client.list_tools()
        # logging.info("Tools available: %s", tools)

        # Build tool description block
        tool_desc = []

        for t in tools:
            name = t.name
            raw_desc = t.description or "No description."
            
            # Extract only the first sentence / first line
            short_desc = raw_desc.strip().split("\n")[0].strip()
            props = t.inputSchema.get("properties", {})

            # Extract param list
            params_list = []
            for p, schema in props.items():
                type_str = extract_type(schema)
                params_list.append(f"{p}: {type_str}")
            params = ", ".join(params_list) if params_list else "no inputs"
            tool_desc.append(f"- {name}: {params} - {short_desc}")
        tool_block = "\n".join(tool_desc)
        # logging.info(tool_block)

        system_prompt = build_system_prompt(tool_block)
        # logging.info(system_prompt)

        prompt = f"{system_prompt}\nUser Question: {prompt}"

        response = await generate_with_timeout(model, prompt)
        if response:
            logging.info("MODEL RAW OUTPUT:")
            logging.info(response.text)
        else:
            logging.error("No output from the model..")
            raise
        
        if response.text.startswith("FUNCTION_CALL:"):
            # execute function-calling
            result = await call_tool_from_model_output(response.text, mcp)
            logging.info(result)
        else:
            # if the answer is straight-forward
            logging.info("FINAL ANSWER: ", response.text)


if __name__ == "__main__":
    # Example 1: 
    prompt = "Create a new product called Hucco ice-cream which costs $100 under Diary Category"
    asyncio.run(demo(prompt))  

    # Example 2: 
    # prompt = "Show me the details of the product with ID 2"
    # asyncio.run(demo(prompt))  

    # Example 3: testing the FASTAPI endpoint function calling (v1 commit)
    # model_output = "FUNCTION_CALL: create_product_products_post|name=Hucco ice-cream|price=100|category=Diary|description=null"
    # result = asyncio.run(call_tool_from_model_output(model_output, mcp))
    # print(result)

    # Example 4: testing the mcp tool function calling (v1 commit)
    # model_output = "FUNCTION_CALL: obtain_product_from_db|product_id=1"
    # result = asyncio.run(call_tool_from_model_output(model_output, mcp))
    # print(result)
