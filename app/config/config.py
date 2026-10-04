from pydantic import BaseModel


class AiOutput(BaseModel):
    image: bytes
    description: str
    shoping_link: str
