from sqlalchemy.orm import Session

from . import models, schemas
from .security import get_password_hash


# User CRUD
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Contact CRUD
def get_contact_by_email(db: Session, email: str):
    return db.query(models.Contact).filter(models.Contact.email == email).first()

def get_contacts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Contact).offset(skip).limit(limit).all()

def create_contact(db: Session, contact: schemas.ContactCreate):
    db_contact = models.Contact(**contact.model_dump())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def get_contact(db: Session, contact_id: int):
    return db.query(models.Contact).filter(models.Contact.id == contact_id).first()

def update_contact(db: Session, contact_id: int, contact: schemas.ContactCreate):
    db_contact = get_contact(db, contact_id)
    if db_contact:
        for key, value in contact.model_dump().items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact

def delete_contact(db: Session, contact_id: int):
    db_contact = get_contact(db, contact_id)
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact

# Group CRUD
def get_group_by_name(db: Session, name: str):
    return db.query(models.Group).filter(models.Group.name == name).first()

def get_groups(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Group).offset(skip).limit(limit).all()

def create_group(db: Session, group: schemas.GroupCreate):
    db_group = models.Group(**group.model_dump())
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

# Template CRUD
def get_template_by_name(db: Session, name: str):
    return db.query(models.Template).filter(models.Template.name == name).first()

def get_templates(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Template).offset(skip).limit(limit).all()

def create_template(db: Session, template: schemas.TemplateCreate):
    db_template = models.Template(**template.model_dump())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

def get_template(db: Session, template_id: int):
    return db.query(models.Template).filter(models.Template.id == template_id).first()

def update_template(db: Session, template_id: int, template: schemas.TemplateCreate):
    db_template = get_template(db, template_id)
    if db_template:
        for key, value in template.model_dump().items():
            setattr(db_template, key, value)
        db.commit()
        db.refresh(db_template)
    return db_template

def delete_template(db: Session, template_id: int):
    db_template = get_template(db, template_id)
    if db_template:
        db.delete(db_template)
        db.commit()
    return db_template

import csv
import io

def create_contacts_from_csv(db: Session, file: io.StringIO):
    reader = csv.reader(file)
    header = next(reader, None)  # Skip header

    contacts_to_add = []
    for row in reader:
        try:
            # Assuming CSV format: email,first_name,last_name
            if len(row) < 3:
                continue # Skip malformed rows

            email, first_name, last_name = row[0], row[1], row[2]

            if not email: # Basic validation
                continue

            # Check if contact already exists to avoid duplicates
            db_contact = get_contact_by_email(db, email=email)
            if db_contact:
                continue

            contact_data = schemas.ContactCreate(
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            contacts_to_add.append(models.Contact(**contact_data.model_dump()))

        except (ValueError, IndexError):
            # Skip rows that don't have enough values
            continue

    db.add_all(contacts_to_add)
    db.commit()
