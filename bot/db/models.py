from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, Integer, Boolean

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
