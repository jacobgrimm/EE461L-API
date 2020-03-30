from sqlalchemy import Column, String, Integer,JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Character(Base):
    __tablename__ = 'Characters'

    id = Column(Integer, primary_key=True)
    HeroName = Column(String(length=255))
    RealName = Column(String(length = 255))
    Aliases = Column(String(length=255))
    Alignment = Column(String(length=255))
    Appearanece = Column(JSON)
    Creators = Column(JSON)
    Deck = Column(String(length=1000))
    Description = Column(String(length=255))
    ImageURL = Column(String(length=255))

    def __init__(self, HeroName, RealName,Aliases,Alignment,Appearance,Creators,Deck,Description,ImageURL):
        self.HeroName = HeroName
        self.RealName = RealName
        self.Aliases = Aliases
        self.Alignment = Alignment
        self.Appearanece = Appearance
        self.Creators = Creators
        self.Deck = Deck
        self.Description = Description
        self.ImageURL = ImageURL

'''
HeroName VARCHAR(255),
RealName VARCHAR(255),
Aliases VARCHAR(255),
Alignment VARCHAR(255),
Appearance json,
Creators json,
Deck VARCHAR(1000),
Description VARCHAR(2000),
FirstAppearance VARCHAR(255),
ImageURL VARCHAR(255));
entryID INT
'''

