from pydantic import BaseModel, Field


class Answer(BaseModel):
    answer:str = Field(description="answer for the question")
    conversation:bool = Field(description="Indicator to know if conversation is ongoing. False if agent has made decision", default=True)

class PurchaseItem(BaseModel):
    name:str = Field(description="name of item")