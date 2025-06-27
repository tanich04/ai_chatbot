from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from bot import build_bot
from langchain_core.messages import HumanMessage

app = FastAPI()
workflow = build_bot()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    messages = body.get("messages", [])
    result = workflow.invoke({"messages": [HumanMessage(content=msg["content"]) for msg in messages]})
    return {"response": result["messages"][-1].content}
