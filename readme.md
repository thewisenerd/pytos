pytos
=====

google photos client library (barely)

how
---

 - go to google credentials page [https://console.developers.google.com/apis/credentials](https://console.developers.google.com/apis/credentials)
 - create new oauth client id
 - download json
 - copy app.cfg.example to app.cfg
 - replace oauth.secrets to json file

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
