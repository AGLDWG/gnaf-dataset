# -*- coding: utf-8 -*-
import _config as config
import psycopg2
from psycopg2 import sql


def test_connect():
    try:
        connect_str = "host='{}' port='{}' dbname='{}' user='{}' password='{}'" \
            .format(
            config.DB_HOST,
            config.DB_PORT,
            config.DB_DBNAME,
            config.DB_USR,
            config.DB_PWD
        )
        conn = psycopg2.connect(connect_str)
        cursor = conn.cursor()
        # get just IDs, ordered, from the address_detail table, paginated by class init args
        #cursor.execute('SELECT address_detail_pid FROM gnaf.address_detail ORDER BY address_detail_pid LIMIT 100;')
        """
        sql = '''SELECT 
                    street_locality_pid, 
                    locality_pid, 
                    building_name || lot_number_prefix || CAST(lot_number AS text) || lot_number_suffix || flat_type || flat_number_prefix || CAST(flat_number AS text) || flat_number_suffix || level_type || level_number_prefix || CAST(level_number AS text) || level_number_suffix || number_first_prefix || CAST(number_first AS text) || number_first_suffix || number_last_prefix || CAST(number_last AS text) || number_last_suffix AS street_detail, 
                    street_name, 
                    locality_name, 
                    state_abbreviation, 
                    postcode
                FROM gnaf.address_view
                WHERE 
                    address_detail_pid = \'%s\''''
        """
        sid = 'GAACT714903383'
        s = sql.SQL('''SELECT 
                    street_locality_pid, 
                    locality_pid, 
                    CAST(number_first AS text), 
                    street_name, street_type_code, 
                    locality_name, 
                    state_abbreviation, 
                    postcode 
                FROM gnaf.address_view 
                WHERE address_detail_pid = {}''')\
            .format(sql.Literal(sid))

        cursor.execute(s)
        rows = cursor.fetchall()
        address_string = "Not found"
        for row in rows:
            address_string = '{} {} {}, {}, {} {}'.format(row[2], row[3].title(), row[4].title(), row[5].title(), row[6], row[7])
            break
        print(address_string)

        s = sql.SQL('''SELECT * FROM codes.geocode LIMIT 1''')
        cursor.execute(s)
        rows = cursor.fetchall()
        p = 'Not founc'
        for row in rows:
            p = row[2]
        print('p: ' + str(p))

    except Exception as e:
        print(e)


if __name__ == '__main__':
    test_connect()
