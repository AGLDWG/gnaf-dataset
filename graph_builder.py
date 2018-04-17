import logging
import _config as config
from psycopg2 import sql
import model.address
import sys


def get_ACT_addresses():
    cursor = config.get_db_cursor()
    s = sql.SQL(
        "SELECT address_detail_pid "
        "FROM gnaf.address_detail "
        "WHERE locality_pid "
        "IN (SELECT locality_pid FROM gnaf.locality WHERE state_pid = '8') "
        "ORDER BY address_detail_pid;")
    cursor.execute(s)

    with open('act_addresses.txt', 'a') as f:
        for row in cursor.fetchall():
            r = config.reg(cursor, row)
            f.write(str(r.address_detail_pid) + '\n')


def run():
    logging.basicConfig(filename='graph_builder.log',
                        level=logging.DEBUG,
                        datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s %(message)s')

    '''
    - For each Address in the Address Register,
    - Create an Address class instance using the ID
    - Serialise that to a file
    '''
    DATA_FILE_LENGTH_MAX = 100000

    cursor = config.get_db_cursor()
    # #  s = sql.SQL('SELECT address_detail_pid FROM gnaf.address_detail ORDER BY address_detail_pid;')
    # s = sql.SQL(
    #     'SELECT address_detail_pid '
    #     'FROM gnaf.address_detail '
    #     'WHERE address_detail_pid >= \'{}\' '
    #     'ORDER BY address_detail_pid;'.format(sys.argv[1]))
    # cursor.execute(s)

    data_file_stem = 'data-'
    data_file_count = int(sys.argv[1])
    # for idx, addr in enumerate(cursor.fetchall()):
    for idx, addr in enumerate(open('faulty.log', 'r').readlines()):
        try:
            # record the Address being processed in case of failure
            # every DATA_FILE_LENGTH_MAXth URI, create a new destination file
            if (idx + 1) % DATA_FILE_LENGTH_MAX == 0:
                data_file_count += 1
            with open(data_file_stem + str(data_file_count).zfill(4) + '.nt', 'a') as fl:
                fl.write(
                    model.address.AddressRenderer(addr.strip(), focus=True, db_cursor=cursor)
                        .export_rdf(view='gnaf', format='text/n3').decode('utf-8')
                )
        except Exception as e:
            logging.log(logging.DEBUG, 'address ' + addr, e)
            print('address ' + addr + '\n')
            print(e)
            with open('faulty2.log', 'a') as f:
                f.write(addr + '\n')
        finally:
            logging.log(logging.INFO, 'Last accessed Address: ' + addr)


if __name__ == '__main__':
    # run()
    get_ACT_addresses()
