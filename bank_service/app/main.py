import os
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from typing import Annotated

from sqlalchemy.orm import Session

from database import database as database
from database.database import ClientDB

from model.client import Client

app = FastAPI()
database.Base.metadata.create_all(bind=database.engine)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/health", status_code=status.HTTP_200_OK)
async def service_alive():
    return {'message': 'service alive'}


@app.get("/get_clients")
async def get_clients(db: db_dependency):
    try:
        result = db.query(ClientDB).limit(100).all()
        return result
    except Exception as e:
        return "Can't access database!"


@app.get("/get_client_by_id")
async def get_client_by_id(client_id: int, db: db_dependency):
    try:
        result = db.query(ClientDB).filter(ClientDB.id == client_id).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail="Client not found")


@app.post("/add_client")
async def add_client(client: Client, db: db_dependency):
    try:
        client_db = ClientDB(
            id=client.id,
            name=client.name,
            currency=client.currency,
            amount=client.amount
        )
        db.add(client_db)
        db.commit()
        return client_db
    except Exception as e:
        raise HTTPException(status_code=404, detail="Client not found")


@app.post("/update_client_currency")
async def update_client_currency(client_id: int, new_currency: str, db: db_dependency):
    try:
        client_db = db.query(ClientDB).filter(ClientDB.id == client_id).first()
        if client_db:
            client_db.currency = new_currency
            db.commit()
            return "Currency updated successfully"
        else:
            raise HTTPException(status_code=404, detail="Client not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/update_client_balance")
async def update_client_balance(client_id: int, amount: float, db: db_dependency):
    try:
        client_db = db.query(ClientDB).filter(ClientDB.id == client_id).first()
        if client_db:
            client_db.amount += amount
            db.commit()
            return "Balance updated successfully"
        else:
            raise HTTPException(status_code=404, detail="Client not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/delete_client")
async def delete_client(client_id: int, db: db_dependency):
    try:
        client_db = db.query(ClientDB).filter(ClientDB.id == client_id).first()
        if client_db:
            db.delete(client_db)
            db.commit()
            return "Success"
        else:
            raise HTTPException(status_code=404, detail="Client not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 80)))
