# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from bot import build_bot
from langchain_core.messages import HumanMessage
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow requests from anywhere (optional: restrict to Streamlit app later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

workflow = build_bot()

class Query(BaseModel):
    question: str

@app.post("/chat")
def chat(req: Query):
    result = workflow.invoke({"messages": [HumanMessage(content=req.question)]})
    return {"response": result["messages"][-1].content}
