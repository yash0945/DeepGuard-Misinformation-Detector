from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/templates",
    tags=["templates"],
)


@router.post("/", response_model=schemas.Template)
def create_template(template: schemas.TemplateCreate, db: Session = Depends(get_db)):
    db_template = crud.get_template_by_name(db, name=template.name)
    if db_template:
        raise HTTPException(status_code=400, detail="Template name already registered")
    return crud.create_template(db=db, template=template)


@router.get("/", response_model=List[schemas.Template])
def read_templates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    templates = crud.get_templates(db, skip=skip, limit=limit)
    return templates


@router.get("/{template_id}", response_model=schemas.Template)
def read_template(template_id: int, db: Session = Depends(get_db)):
    db_template = crud.get_template(db, template_id=template_id)
    if db_template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return db_template


@router.put("/{template_id}", response_model=schemas.Template)
def update_template(
    template_id: int, template: schemas.TemplateCreate, db: Session = Depends(get_db)
):
    db_template = crud.update_template(db, template_id=template_id, template=template)
    if db_template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return db_template


@router.delete("/{template_id}", response_model=schemas.Template)
def delete_template(template_id: int, db: Session = Depends(get_db)):
    db_template = crud.delete_template(db, template_id=template_id)
    if db_template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return db_template
