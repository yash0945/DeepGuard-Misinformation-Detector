from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table,
    DateTime,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Association table for many-to-many relationship between contacts and groups
contact_group_association = Table(
    "contact_group",
    Base.metadata,
    Column("contact_id", Integer, ForeignKey("contacts.id"), primary_key=True),
    Column("group_id", Integer, ForeignKey("groups.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    # This column can store additional personalized data as a JSON string
    custom_fields = Column(String)
    groups = relationship(
        "Group", secondary=contact_group_association, back_populates="contacts"
    )


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    contacts = relationship(
        "Contact", secondary=contact_group_association, back_populates="groups"
    )


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    subject = Column(String)
    body = Column(String)


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    # broadcast, cluster, personalized
    mode = Column(String, nullable=False)
    # immediate, scheduled
    status = Column(String, nullable=False)
    scheduled_time = Column(DateTime(timezone=True), server_default=func.now())
    template_id = Column(Integer, ForeignKey("templates.id"))
    template = relationship("Template")
    # For cluster mode, we might need a mapping of group to template
    # For now, let's keep it simple


class DeliveryLog(Base):
    __tablename__ = "delivery_logs"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    campaign = relationship("Campaign")
    contact_id = Column(Integer, ForeignKey("contacts.id"))
    contact = relationship("Contact")
    sent_time = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String)  # e.g., 'sent', 'failed'
