pytos
=====

google photos client library (barely)

how
---

 - go to google credentials page [https://console.developers.google.com/apis/credentials](https://console.developers.google.com/apis/credentials)
 - create new oauth client id
 - download json
 - copy config.toml.example to config.toml
 - replace oauth.secrets to downloaded json file

why
---

so that I could do this:

```
pip3 install --user -r requirements.txt
python3 -m pytos init
sqlite3 app.db
> select * from media_item where not exists(select * from album_item where media_item_id = id);
```
