from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .database import create_db_and_tables
from .routers import auth, pages, contacts, templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth.router)
app.include_router(pages.router)
app.include_router(contacts.router)
app.include_router(templates.router)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
