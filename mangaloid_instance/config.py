from os import getenv

class Config:
    def __init__(self):
        self.database = getenv("DB_PATH", "mangaloid.db")
        self.http_port = int(getenv("HTTP_PORT", "1337"))
        self.admin_ips = [i.strip() for i in getenv("ADMIN_IPS", "").split(",")]
        
        self.instance_name = getenv("INSTANCE_NAME")
        self.instance_address = getenv("INSTANCE_ADDRESS")
        self.instance_operator = getenv("INSTANCE_OPERATOR")
        self.instance_icon = getenv("INSTANCE_ICON")
        self.instance_description = getenv("INSTANCE_DESCRIPTION")

        self.upload_ipfs_node = getenv("UPLOAD_IPFS", "127.0.0.1")
        self.thumbnail_path = getenv("THUMBNAIL_PATH", "~/mangaloid_thumbnails")
        self.max_tags = int(getenv("MAX_TAGS", "5"))
        self.max_results = int(getenv("MAX_RESULTS", 50))

config = Config()