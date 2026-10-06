from pydantic import BaseModel


class CVResponse(BaseModel):
    id: str
    name: str
    file_name: str | None = None
    created_at: str