from version import VERSION

class Instance:
    """A class that holds instance information. Look at the documentation about more information regarding instances. """
    @classmethod
    def from_dict(cls, dc):
        return cls(
            dc['name'],
            dc['operator'],
            dc['icon'],
            dc['description'],
            dc['version']
        )

    def __init__(self, name, operator, icon, description="", version=VERSION):
        self.name = name
        self.operator = operator
        self.version = version
        self.icon = icon
        self.description = description
        self.version = version

    def to_dict(self):
        return {
            "name" : self.name,
            "operator" : self.operator,
            "icon" : self.icon,
            "description" : self.description,
            "version" : self.version
        }
