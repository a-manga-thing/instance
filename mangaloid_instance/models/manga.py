class Manga:
    def __init__(self, database_result, creators=None):
        self.manga_id = database_result["manga_id"]
        self.titles = [i.strip() for i in database_result["titles"].split(",")]
        self.description = database_result["description"]
        self.creators = creators or [database_result["creator_name"]]

    def to_dict(self):
        return {
            "manga_id" : self.manga_id,
            "titles" : self.titles,
            "description": self.description,
            "creators": self.creators
        }

    def __str__(self):
        return self.titles[0]
