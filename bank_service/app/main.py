import os
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Form
from typing import Annotated

from sqlalchemy.orm import Session

from database import database as database
from database.database import ClientDB

from model.client import Client
from keycloak import KeycloakOpenID

app = FastAPI()
database.Base.metadata.create_all(bind=database.engine)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

KEYCLOAK_URL = "http://keycloak:8080/"
KEYCLOAK_CLIENT_ID = "testClient"
KEYCLOAK_REALM = "testRealm"
KEYCLOAK_CLIENT_SECRET = "ZMCmwO1QwvOkhRXayXMWA2l32u9FAXCT"

user_token = ""
keycloak_openid = KeycloakOpenID(server_url=KEYCLOAK_URL,
                                  client_id=KEYCLOAK_CLIENT_ID,
                                  realm_name=KEYCLOAK_REALM,
                                  client_secret_key=KEYCLOAK_CLIENT_SECRET)

###########
#Prometheus
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    try:
        # Получение токена
        token = keycloak_openid.token(grant_type=["password"],
                                      username=username,
                                      password=password)
        global user_token
        user_token = token
        return token
    except Exception as e:
        print(e)  # Логирование для диагностики
        raise HTTPException(status_code=400, detail="Не удалось получить токен")

def user_got_role():
    global user_token
    token = user_token
    try:
        userinfo = keycloak_openid.userinfo(token["access_token"])
        token_info = keycloak_openid.introspect(token["access_token"])
        if "testRole" not in token_info["realm_access"]["roles"]:
            raise HTTPException(status_code=403, detail="Access denied")
        return token_info
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token or access denied")

@app.get("/health", status_code=status.HTTP_200_OK)
async def service_alive():
    if (user_got_role()):
        return {'message': 'service alive'}
    else:
        return "Wrong JWT Token"


@app.get("/get_clients")
async def get_clients(db: db_dependency):
    if (user_got_role()):
        try:
            result = db.query(ClientDB).limit(100).all()
            return result
        except Exception as e:
            return "Can't access database!"
    else:
        return "Wrong JWT Token"

@app.get("/get_client_by_id")
async def get_client_by_id(client_id: int, db: db_dependency):
    if (user_got_role()):
        try:
            result = db.query(ClientDB).filter(ClientDB.id == client_id).first()
            return result
        except Exception as e:
            raise HTTPException(status_code=404, detail="Client not found")
    else:
        return "Wrong JWT Token"

@app.post("/add_client")
async def add_client(client: Client, db: db_dependency):
    if (user_got_role()):
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
    else:
        return "Wrong JWT Token"

@app.post("/update_client_currency")
async def update_client_currency(client_id: int, new_currency: str, db: db_dependency):
    if (user_got_role()):
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
    else:
        return "Wrong JWT Token"

@app.post("/update_client_balance")
async def update_client_balance(client_id: int, amount: float, db: db_dependency):
    if (user_got_role()):
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
    else:
        return "Wrong JWT Token"

@app.delete("/delete_client")
async def delete_client(client_id: int, db: db_dependency):
    if (user_got_role()):
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
    else:
        return "Wrong JWT Token"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 80)))
