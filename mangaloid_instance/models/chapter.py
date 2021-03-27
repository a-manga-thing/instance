
class Chapter:
    def __init__(self, database_result):
        self.manga_id = database_result["manga_id"]
        self.title = database_result["title"]
        self.number = database_result["number"]
        self.page_count = database_result["page_count"]
        self.image_id = database_result["image_id"]

    def to_dict(self):
        return {
            "manga_id" : self.manga_id,
            "title" : self.title,
            "number" : self.number,
            "page_count" : self.page_count,
            "image_id" : self.image_id
        }