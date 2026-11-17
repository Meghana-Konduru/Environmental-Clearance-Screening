
import os
import asyncio

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Stub LLM")


class GenerateRequest(BaseModel):
    prompt: str


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/generate")
async def generate(request: GenerateRequest):
    delay = float(os.getenv("STUB_DELAY_SECONDS", "2"))

    await asyncio.sleep(delay)

    return {
        "response": "This is a simulated LLM response.",
        "stub": True,
        "prompt_length": len(request.prompt)
    }
