from fastapi import FastAPI
from pydantic import BaseModel
from bot import build_bot
from langchain_core.messages import HumanMessage
import logging

app = FastAPI()
workflow = build_bot()

logging.basicConfig(level=logging.INFO)

class Query(BaseModel):
    question: str

@app.post("/chat")
def chat(req: Query):
    logging.info(f"Incoming: {req.question}")
    result = workflow.invoke({"messages": [HumanMessage(content=req.question)]})
    return {"response": result["messages"][-1].content}
