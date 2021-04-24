# Mangaloid Instance
## Reference Implementation (Python/aiohttp/sqlalchemy)

### TODO:
- Scanlation groups table
- Add ActivityPub integration, Instance subscribing and keeping as well as relevant routes  

   


## API Reference

### Manga Routes
| Name | Parameteres |  Result
|---|---|---|
/info | | Instance
/manga/search | String: __title__, String: __author__, String: __artist__, String: __genres[]__ | Manga[]
/manga/from_id | Integer: __id__ | Manga
/manga/get_chapters | Integer: __id__ | Chapter[]
/manga/thumbnail | Integer: __id__ | Image
---
__Parameters are passed as URL-encoded GET parameters__
__Multiple genres should be CSV__   
   
__Search help__  
```
Searches manga database based on title, author, artist and genres/tags
All of these are optional, can be used in any combination and are evaluated
in that specific order.
Args:
    title (str): This is tested in a case-insensitive LIKE clause.
    author (str): This is tested as "equals" and is case-sensitive.
    artist (str): This is tested as "equals" and is case-sensitive.
    tags (list): List of genres/tags. Can be prefixed with either + or -
                    to define inclusion/exclusion (if missing it defaults to +).
                    As for the tags themselves they are tested as "equal" 
                    and are case-sensitive.
```  
   

### Admin Routes
__POST__ `/admin/add_manga` -> `{"id" : int}`
```
Args (* means mandatory):
    type: Manga, Webtoon. Defaults to Manga
    *country_of_origin (str) : ISO-3166 Country Code
    *publication_status (str): Ongoing, Axed, Completed
    *scanlation_status (bool): Is completely scanlated
    mal_id (int): MyAnimeList ID
    anilist_id (int): AniList ID
    mu_id (int): MangaUpdates ID
```

__POST__ `/admin/add_chapter` -> Chapter
```
Args (* means mandatory):
    *chapter_no (int)
    chapter_postfix (str)
    *page_count (int)
    *title (str)
    version (int)
    *language (str) : ISO 639-1 Language code
    date_added (datetime): Defaults to current datetime
    *ipfs_link (str): IPFS CID to chapter directory
```

### Return types

#### __Manga__
```json
{
    "id": int, 
    "type": str, // Manga / Webtoon
    "titles": [str],
    "artists": [str],
    "authors": [str],
    "genres": [str],
    "country_of_origin": str, // (ISO-3166)
    "publication_status": str, // Ongoing, Axed, Completed
    "scanlation_status": bool,
    "mal_id": int,
    "anilist_id": int,
    "mangaupdates_id": int
}
```

#### __Chapter__
```json
{
    "id": int,
    "manga_id": int,
    "chapter_no": int,
    "chapter_postfix": str,
    "ordinal": int,
    "title": str,
    "page_count": int,
    "version": int,
    "language_id": str, // ISO 639-1
    "group_id": int,
    "date_added": int, // UTC Unix Timestamp
    "ipfs_link": str
}
```
