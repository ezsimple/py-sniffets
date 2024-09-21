from pydantic import BaseModel

class Image(BaseModel):
    filename: str
    title: str

