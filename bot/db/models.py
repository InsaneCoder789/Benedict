from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, Integer

Base = declarative_base()


class Member(Base):
    __tablename__ = "members"

    base_level_requirement = 5000
    level_requirement_factor = 150

    id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, nullable=False)
    xp = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=0, nullable=False)
