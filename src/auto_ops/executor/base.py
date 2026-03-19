from pydantic import BaseModel


class ExecutionResult(BaseModel):
    action: str
    ok: bool
    performed: bool
    detail: str = ""
