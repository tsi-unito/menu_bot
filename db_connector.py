# TODO: add to docker: sudo apt install libmariadb3 libmariadb-dev
# TODO, passare a sqlAlchemy
import mariadb

USER = "bot"
PASSWD = "bot"
HOST = "127.0.0.1"
PORT = 3306
DB = "bot"


def init():
    # Connect to MariaDB Platform
    try:
        conn = mariadb.connect(
            user=USER,
            password=PASSWD,
            host=HOST,
            port=PORT,
            database=DB
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        return

    # Get Cursor
    cur = conn.cursor()
    # create tables
    cur.execute("CREATE TABLE IF NOT EXISTS subscription ("
                "uid INT PRIMARY KEY,"
                "sub_dubai BOOLEAN NOT NULL DEFAULT FALSE,"
                "sub_doc BOOLEAN NOT NULL DEFAULT FALSE);")
    cur.execute("CREATE TABLE IF NOT EXISTS menu ("
                "resturant VARCHAR(5) PRIMARY KEY,"
                "menu LONGTEXT NOT NULL);")


def add_user(uid):
    try:
        conn = mariadb.connect(
            user=USER,
            password=PASSWD,
            host=HOST,
            port=PORT,
            database=DB
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        return

    cur = conn.cursor()

    cur.execute("INSERT IGNORE INTO subscription (uid) VALUES (?);", (uid,)) # ignore if already exists

    conn.commit()


def add_subscription(uid, resturant):
    try:
        conn = mariadb.connect(
            user=USER,
            password=PASSWD,
            host=HOST,
            port=PORT,
            database=DB
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        return

    cur = conn.cursor()

    if resturant == "dubai":
        cur.execute("UPDATE subscription SET sub_dubai = ? WHERE uid = ?;", (True, uid))
    elif resturant == "doc":
        cur.execute("UPDATE subscription SET sub_doc = ? WHERE uid = ?;", (True, uid))

    conn.commit()

def is_subscribed(uid, resturant):
    try:
        conn = mariadb.connect(
            user=USER,
            password=PASSWD,
            host=HOST,
            port=PORT,
            database=DB
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        return

    cur = conn.cursor()

    if resturant == "dubai":
        cur.execute("SELECT sub_dubai FROM subscription WHERE uid = ?;", (uid,))
    elif resturant == "doc":
        cur.execute("SELECT sub_doc FROM subscription WHERE uid = ?;", (uid,))

    return cur.fetchone()[0]

def remove_subscription(uid, resturant):
    try:
        conn = mariadb.connect(
            user=USER,
            password=PASSWD,
            host=HOST,
            port=PORT,
            database=DB
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        return

    cur = conn.cursor()

    if resturant == "dubai":
        cur.execute("UPDATE subscription SET sub_dubai = ? WHERE uid = ?;", (False, uid))
    elif resturant == "doc":
        cur.execute("UPDATE subscription SET sub_doc = ? WHERE uid = ?;", (False, uid))

    conn.commit()

def get_subscribers(resturant):
    try:
        conn = mariadb.connect(
            user=USER,
            password=PASSWD,
            host=HOST,
            port=PORT,
            database=DB
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        return

    cur = conn.cursor()

    if resturant == "dubai":
        cur.execute("SELECT uid FROM subscription WHERE sub_dubai = ?;", (True,))
    elif resturant == "doc":
        cur.execute("SELECT uid FROM subscription WHERE sub_doc = ?;", (True,))
    else:
        cur.execute("SELECT uid,sub_doc,sub_dubai FROM subscription WHERE sub_doc = ? OR sub_dubai = ?;", (True, True))

    return cur.fetchall()

if __name__ == "__main__":
    init()
    add_user(123)
    add_subscription(123, "dubai")
    print(is_subscribed(123, "dubai"))
    remove_subscription(123, "dubai")
    print(get_subscribers("dubai"))
    print(is_subscribed(123, "dubai"))


