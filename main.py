from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from bot import build_bot

app = FastAPI()
workflow = build_bot()

class Query(BaseModel):
    message: str

@app.post("/chat")
def chat(req: Query):
    result = workflow.invoke({"messages": [HumanMessage(content=req.message)]})
    return {"response": result["messages"][-1].content}
