

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

import csv
import io

def create_contacts_from_csv(db: Session, file: io.StringIO):
    reader = csv.reader(file)
    header = next(reader, None)
    contacts_to_add = []
    for row in reader:
        try:
            if len(row) < 3: continue
            email, first_name, last_name = row[0], row[1], row[2]
            if not email or get_contact_by_email(db, email=email): continue
            contact_data = schemas.ContactCreate(email=email, first_name=first_name, last_name=last_name)
            contacts_to_add.append(models.Contact(**contact_data.model_dump()))
        except (ValueError, IndexError):
            continue
    db.add_all(contacts_to_add)
    db.commit()

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

def get_group(db: Session, group_id: int):
    return db.query(models.Group).filter(models.Group.id == group_id).first()

def delete_group(db: Session, group_id: int):
    db_group = get_group(db, group_id)
    if db_group:
        db.delete(db_group)
        db.commit()
    return db_group

def add_contact_to_group(db: Session, group_id: int, contact_id: int):
    group = get_group(db, group_id)
    contact = get_contact(db, contact_id)
    if group and contact and contact not in group.contacts:
        group.contacts.append(contact)
        db.commit()
    return group

def remove_contact_from_group(db: Session, group_id: int, contact_id: int):
    group = get_group(db, group_id)
    contact = get_contact(db, contact_id)
    if group and contact and contact in group.contacts:
        group.contacts.remove(contact)
        db.commit()
    return group

# SMTP Settings CRUD
def get_smtp_settings(db: Session):
    # There should only ever be one row
    return db.query(models.SMTPSettings).first()

def update_smtp_settings(db: Session, settings: schemas.SMTPSettingsCreate):
    db_settings = get_smtp_settings(db)
    update_data = settings.model_dump(exclude_unset=True)

    # Don't overwrite password with an empty value if it's not provided
    if 'password' in update_data and not update_data['password']:
        del update_data['password']

    if db_settings:
        for key, value in update_data.items():
            setattr(db_settings, key, value)
    else:
        db_settings = models.SMTPSettings(**update_data)
        db.add(db_settings)

    db.commit()
    db.refresh(db_settings)
    return db_settings

# Campaign CRUD
def create_campaign(db: Session, name: str, mode: str, status: str):
    campaign = models.Campaign(name=name, mode=mode, status=status)
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign

def update_campaign_status(db: Session, campaign_id: int, status: str):
    campaign = db.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()
    if campaign:
        campaign.status = status
        db.commit()
    return campaign

# Delivery Log CRUD
def create_delivery_log(db: Session, campaign_id: int, contact_id: int, status: str):
    log = models.DeliveryLog(campaign_id=campaign_id, contact_id=contact_id, status=status)
    db.add(log)
    db.commit()
    return log

# Reporting CRUD
def get_campaigns(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Campaign).order_by(models.Campaign.id.desc()).offset(skip).limit(limit).all()

def get_delivery_logs(db: Session, skip: int = 0, limit: int = 1000):
    # Eager load related data to avoid N+1 query problem
    return db.query(models.DeliveryLog).options(
        db.joinedload(models.DeliveryLog.campaign),
        db.joinedload(models.DeliveryLog.contact)
    ).order_by(models.DeliveryLog.id.desc()).offset(skip).limit(limit).all()
