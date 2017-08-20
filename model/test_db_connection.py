import _config as config
import psycopg2


def test_connect():
    try:
        connect_str = "host='{}' dbname='{}' user='{}' password='{}'" \
            .format(
            config.DB_HOST,
            config.DB_DBNAME,
            config.DB_USR,
            config.DB_PWD
        )
        conn = psycopg2.connect(connect_str)
        cursor = conn.cursor()
        # get just IDs, ordered, from the address_detail table, paginated by class init args
        cursor.execute('SELECT address_detail_pid FROM gnaf.address_detail ORDER BY address_detail_pid LIMIT 100;')
        rows = cursor.fetchall()
        print(rows)
    except Exception as e:
        print("Uh oh, can't connect to DB. Invalid dbname, user or password?")
        print(e)


if __name__ == '__main__':
    test_connect()
