from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from wizard.agent import DatabaseWizard

load_dotenv()

app = FastAPI(
    title="Database LLM Wizard",
    description="A shamanic coder's bridge between intention and database reality",
    version="1.0.0",
)


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    question: str
    answer: str


wizard = DatabaseWizard()


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest) -> AskResponse:
    try:
        answer = await wizard.process(request.question)
        return AskResponse(question=request.question, answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/")
async def root():
    return {"message": "Database LLM Wizard is awakened"}
