DATABASE_CREATION = [
    """
    CREATE TABLE IF NOT EXISTS "manga" (
        "manga_id"	INTEGER NOT NULL,
        "titles"	TEXT NOT NULL,
        "description"	TEXT,
        PRIMARY KEY("manga_id")
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS "creators" (
	    "manga_id"	INTEGER NOT NULL,
	    "name"	TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS "chapters" (
        "manga_id"	INTEGER NOT NULL,
        "number"	REAL NOT NULL,
        "page_count"	INTEGER NOT NULL,
        "image_id"	TEXT NOT NULL
    );
    """
]

QUERIES = {
    "MANGA_BY_ID": """
        SELECT manga.*, creators.creator_name FROM manga 
        INNER JOIN creators ON manga.manga_id == creators.manga_id
        WHERE manga.manga_id == ?
    """,
    "TITLE_SEARCH": """
        SELECT manga.*, creators.creator_name FROM manga 
        INNER JOIN creators ON manga.manga_id == creators.manga_id
        WHERE manga.titles LIKE ?
    """,
    "CREATOR_SEARCH": """
        SELECT manga.*, creators.creator_name FROM manga 
        INNER JOIN creators ON manga.manga_id == creators.manga_id
        WHERE {}
    """
}