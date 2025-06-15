from fastapi import FastAPI
from pydantic import BaseModel
from fastapi_mcp import FastApiMCP
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()

@app.get("/add", operation_id="add_two_numbers")
async def add(a: int, b: int):
    """Add two numbers and return the sum."""
    summ = pd.DataFrame({"a": [a], "b": [b], "sum": [a+b]})
    result = int(summ.loc[0, "sum"])
    return {"sum": result}

mcp = FastApiMCP(
    app,
    name="Addition MCP",
    description="Simple API exposing adding operation",
)

mcp.mount()