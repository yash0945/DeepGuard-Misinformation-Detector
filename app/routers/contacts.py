from typing import List
import io

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/contacts",
    tags=["contacts"],
)


@router.post("/", response_model=schemas.Contact)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    db_contact = crud.get_contact_by_email(db, email=contact.email)
    if db_contact:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_contact(db=db, contact=contact)


@router.get("/", response_model=List[schemas.Contact])
def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = crud.get_contacts(db, skip=skip, limit=limit)
    return contacts


@router.get("/{contact_id}", response_model=schemas.Contact)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = crud.get_contact(db, contact_id=contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@router.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type != 'text/csv':
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV.")

    contents = await file.read()
    string_io = io.StringIO(contents.decode("utf-8"))

    crud.create_contacts_from_csv(db, file=string_io)

    return {"message": "CSV file processed successfully"}


@router.put("/{contact_id}", response_model=schemas.Contact)
def update_contact(
    contact_id: int, contact: schemas.ContactCreate, db: Session = Depends(get_db)
):
    db_contact = crud.update_contact(db, contact_id=contact_id, contact=contact)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@router.delete("/{contact_id}", response_model=schemas.Contact)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = crud.delete_contact(db, contact_id=contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact
