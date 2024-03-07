from pydantic import BaseModel, ConfigDict
from typing import Optional


class Client(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    name: str
    currency: str
    amount: float