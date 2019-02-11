pytos
=====

google photos client library (barely)

why
---

so that I could do this:

```
pip install --user -r requirements.txt 
./app init_library
./app init_albums
./app albums_meta
sqlite3 app.db
> select id from mediaitems where id not in (select id from albums_meta);
```
