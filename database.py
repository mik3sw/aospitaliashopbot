# database che gestisce gli utenti iscritti al bot
import sqlite3


def run_query(query):
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    cur.execute(query)
    con.commit()
    con.close()


def generate_blacklist_table():
    # tabella con solo id_telegram degli utenti
    con = sqlite3.connect("blacklist.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS blacklist(telegram_id int NOT NULL PRIMARY KEY UNIQUE);")
    con.commit()
    con.close()


def add_blacklist(tg_id):
    con = sqlite3.connect("blacklist.db")
    cur = con.cursor()
    cur.execute("INSERT INTO blacklist(telegram_id) VALUES({});".format(tg_id))
    con.commit()
    con.close()


def add_user(id):
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    cur.execute("INSERT INTO users(telegram_id) VALUES({});".format(id))
    con.commit()
    con.close()


def get_id(id):
    con = sqlite3.connect("blacklist.db")
    cur = con.cursor()
    cursor = con.execute(f"SELECT telegram_id FROM blacklist WHERE telegram_id = {id}")
    for res in cursor:
        user = res[0]
    return user


def delete_from_blacklist(tg_id):
    query = "DELETE from blacklist WHERE telegram_id = {};".format(tg_id)
    con = sqlite3.connect("blacklist.db")
    cur = con.cursor()
    cur.execute(query)
    con.commit()
    con.close()


def generate_posts_table():
    con = sqlite3.connect("posts.db")
    cur = con.cursor()
    query="CREATE TABLE IF NOT EXISTS posts(telegram_id INTEGER NOT NULL PRIMARY KEY UNIQUE, type text, name text,description text,price text,payments text,shipment text,contacts text);"
    cur.execute(query)
    con.commit()
    con.close()


def add_post(telegram_id):

    query = f"INSERT INTO posts (telegram_id) VALUES ({telegram_id})"
    con = sqlite3.connect("posts.db")
    cur = con.cursor()
    cur.execute(query)
    con.commit()
    con.close()


def add_post_partial(tg_id, name, value, value_type="text"):
    if value_type == "text":
        value = value.replace("\"", "'")
        query = "UPDATE posts set {} = \"{}\" where telegram_id = {}".format(name, value, tg_id, )
    else:
        query = "INSERT INTO posts ({}) VALUES ({})"
    con = sqlite3.connect("posts.db")
    cur = con.cursor()
    cur.execute(query)
    con.commit()
    con.close()


def delete_previous_post(tg_id):
    query = "DELETE from posts WHERE telegram_id = {};".format(tg_id)


def getpost(tg_id):
    conn = sqlite3.connect("posts.db")
    cursor = conn.execute(f"SELECT * FROM posts WHERE telegram_id = {tg_id}")

    for res in cursor:
        res2 = {
            "tg_id": res[0],
            "post": res[1],
            "name": res[2],
            "description": res[3],
            "price": res[4],
            "payments": res[5],
            "shipment": res[6],
            "contacts": res[7],
        }
    return res2


def testout(db):
    conn = sqlite3.connect(f"{db}.db")
    cursor = conn.execute(f"SELECT * FROM {db};")

    for row in cursor:
        print(row)
        print("\n")

    conn.commit()
    conn.close() 


generate_posts_table()
generate_blacklist_table()