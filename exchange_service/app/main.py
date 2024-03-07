import os
from typing import List

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi import status
from pydantic import BaseModel

app = FastAPI()

exchange_rates = {
    "USD": {
        "EUR": 0.85,
        "GBP": 0.73,
        "JPY": 110.32
    },
    "EUR": {
        "USD": 1.18,
        "GBP": 0.86,
        "JPY": 129.74
    },
    "GBP": {
        "USD": 1.37,
        "EUR": 1.16,
        "JPY": 150.99
    },
    "JPY": {
        "USD": 0.0091,
        "EUR": 0.0077,
        "GBP": 0.0066
    }
}


class CurrencyConversionRequest(BaseModel):
    amount: float
    from_currency: str
    to_currency: str


@app.get("/health", status_code=status.HTTP_200_OK)
async def service_alive():
    return {'message': 'service alive'}


@app.get("/available_currencies", response_model=List[str])
async def get_available_currencies():
    return list(exchange_rates.keys())


@app.post("/convert_currency")
async def convert_currency(request: CurrencyConversionRequest):
    if request.from_currency not in exchange_rates or request.to_currency not in exchange_rates[request.from_currency]:
        raise HTTPException(status_code=400, detail="Invalid currency pair")

    conversion_rate = exchange_rates[request.from_currency][request.to_currency]
    converted_amount = request.amount * conversion_rate

    result = {
        "amount": request.amount,
        "from_currency": request.from_currency,
        "to_currency": request.to_currency,
        "converted_amount": round(converted_amount, 2)
    }
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 80)))
