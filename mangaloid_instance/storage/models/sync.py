from sqlalchemy import Column, Text
from . import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    address = Column(Text, unique=True, primary_key=True)
    private_key = Column(Text)
    public_key = Column(Text)


class Instance(Base):
    """A class that holds instance information. Look at the documentation about more information regarding instances. """
    __tablename__ = "instances"

    name = Column(Text, primary_key=True)
    address = Column(Text, primary_key=True, unique=True)
    operator = Column(Text)
    description = Column(Text)
    icon = Column(Text)
    version = Column(Text)
    public_key = Column(Text)

    def to_dict(self):
        return {
            "name" : self.name,
            "address" : self.address,
            "operator" : self.operator,
            "icon" : self.icon,
            "description" : self.description,
            "version" : self.version,
            "public_key" : self.public_key
        }