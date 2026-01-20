from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    domain = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Subreddit(Base):
    __tablename__ = "subreddits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    subscribers = Column(Integer, default=0)
    description = Column(Text, default="")
    business_value_score = Column(Float, default=0.0)
    relevance_score = Column(Float, default=0.0)
    engagement_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    canonical_name = Column(String, index=True)
    entity_type = Column(String, default="unknown")  # person, company, product, etc.
    confidence_score = Column(Float, default=0.5)
    created_at = Column(DateTime, default=datetime.utcnow)

    mentions = relationship("EntityMention", back_populates="entity", cascade="all, delete-orphan")


class EntityMention(Base):
    __tablename__ = "entity_mentions"

    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(Integer, ForeignKey("entities.id"))
    mention_text = Column(String)
    context = Column(Text)
    source_url = Column(String, default="")
    confidence_score = Column(Float, default=0.5)
    created_at = Column(DateTime, default=datetime.utcnow)

    entity = relationship("Entity", back_populates="mentions")


class Relationship(Base):
    __tablename__ = "relationships"

    id = Column(Integer, primary_key=True, index=True)
    subject_entity_id = Column(Integer, ForeignKey("entities.id"))
    object_entity_id = Column(Integer, ForeignKey("entities.id"))
    relationship_type = Column(String)
    confidence_score = Column(Float, default=0.5)
    source_text = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    subject = relationship("Entity", foreign_keys=[subject_entity_id])
    object = relationship("Entity", foreign_keys=[object_entity_id])
