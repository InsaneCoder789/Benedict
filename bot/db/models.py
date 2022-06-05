from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Integer,
    DateTime,
    Boolean,
)
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class GuildSettings(Base):
    __tablename__ = "guild_settings"

    guild_id = Column(BigInteger, primary_key=True)

    levels_channel = Column(BigInteger, nullable=True)
    levels_enabled = Column(Boolean, default=True, nullable=False)


class Member(Base):
    __tablename__ = "members"

    base_level_requirement = 5000
    level_requirement_factor = 150

    user_id = Column(BigInteger, nullable=False, primary_key=True)
    guild_id = Column(BigInteger, nullable=False, primary_key=True)
    xp = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=0, nullable=False)


class Infraction(Base):
    __tablename__ = "infractions"

    id = Column(String, primary_key=True)
    guild_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    moderator_id = Column(BigInteger, nullable=False)
    reason = Column(String, nullable=False)


class Webhook(Base):
    __tablename__ = "webhooks"

    channel_id = Column(BigInteger, primary_key=True)
    webhook_url = Column(String, nullable=False)


class ImpersonationLog(Base):
    __tablename__ = "impersonation_logs"

    id = Column(String, primary_key=True)
    guild_id = Column(BigInteger, nullable=False)
    channel_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    impersonator_id = Column(BigInteger, nullable=False)
    message = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class AFK(Base):
    __tablename__ = "afks"

    id = Column(String, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
