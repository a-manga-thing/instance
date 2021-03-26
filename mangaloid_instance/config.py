from os import getenv

class Config:
    def __init__(self):
        self.database = getenv("DB_PATH", "mangaloid.db")
        self.http_port = int(getenv("HTTP_PORT", "1337"))
        
        self.instance_name = getenv("INSTANCE_NAME")
        self.instance_operator = getenv("INSTANCE_OPERATOR")
        self.instance_icon = getenv("INSTANCE_ICON")
        self.instance_description = getenv("INSTANCE_DESCRIPTION")

config = Config()