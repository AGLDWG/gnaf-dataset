import logging

from psycopg2 import sql

import _config as config
from db import get_db_cursor, reg
import model.address
import model.locality

dbschema=sql.Identifier(config.DB_SCHEMA)

def get_state_addresses(state_pid):
    with get_db_cursor() as cursor:
        s = sql.SQL('''SELECT address_detail_pid 
               FROM {dbschema}.address_detail 
               WHERE locality_pid 
               IN (SELECT locality_pid FROM gnaf.locality WHERE state_pid = {pid}) 
               ORDER BY address_detail_pid;''').format(pid=sql.Literal(state_pid), dbschema=dbschema)
        cursor.execute(s)

    with open('addresses_state_{}.txt'.format(state_pid), 'w') as f:
        for row in cursor.fetchall():
            r = reg(cursor, row)
            f.write(str(r.address_detail_pid) + '\n')


def get_state_localities(state_pid):
    with get_db_cursor() as cursor:
        s = sql.SQL('''SELECT locality_pid 
               FROM {dbschema}.locality WHERE state_pid = {pid}
               ORDER BY locality_pid;''').format(pid=sql.Literal(state_pid), dbschema=dbschema)
        cursor.execute(s)

    with open('localities_state_{}.txt'.format(state_pid), 'w') as f:
        for row in cursor.fetchall():
            r = reg(cursor, row)
            f.write(str(r.locality_pid) + '\n')


def run_addresses(index_file, file_id, data_file_count):
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

    with get_db_cursor() as cursor:
        data_file_stem = 'data-address-'+str(file_id)+"-"
        # for idx, addr in enumerate(cursor.fetchall()):
        for idx, addr in enumerate(open(index_file, 'r').readlines()):
            a = addr.strip()
            try:
                # record the Address being processed in case of failure
                # every DATA_FILE_LENGTH_MAXth URI, create a new destination file
                if (idx + 1) % DATA_FILE_LENGTH_MAX == 0:
                    data_file_count += 1
                with open(data_file_stem + str(data_file_count).zfill(4) + '.nt', 'a') as fl:
                    fl.write(
                        model.address.Address(a, focus=True, db_cursor=cursor)
                            .export_rdf(view='gnaf').serialize(format='nt').decode('utf-8')
                    )
            except Exception as e:
                logging.log(logging.DEBUG, 'address ' + a, e)
                print('address ' + a + '\n')
                print(e)
                with open('faulty.log', 'a') as f:
                    f.write(addr + '\n')
            finally:
                logging.log(logging.INFO, 'Last accessed Address: ' + a)


def run_localities(locality_index_file, file_id, data_file_count):
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

    with get_db_cursor() as cursor:
        data_file_stem = 'data-locality-'+str(file_id)+"-"
        # for idx, addr in enumerate(cursor.fetchall()):
        for idx, addr in enumerate(open(locality_index_file, 'r').readlines()):
            a = addr.strip()
            try:
                # record the Address being processed in case of failure
                # every DATA_FILE_LENGTH_MAXth URI, create a new destination file
                if (idx + 1) % DATA_FILE_LENGTH_MAX == 0:
                    data_file_count += 1
                with open(data_file_stem + str(data_file_count).zfill(4) + '.nt', 'a') as fl:
                    rdf = model.locality.Locality(a, db_cursor=cursor)\
                        .export_rdf(view='gnaf').serialize(format='nt').decode('utf-8')
                    print(rdf)
                    fl.write(
                        rdf
                    )
            except Exception as e:
                logging.log(logging.DEBUG, 'address ' + a, e)
                print('locality ' + a + '\n')
                print(e)
                with open('faulty_locality.log', 'a') as f:
                    f.write(addr + '\n')
            finally:
                logging.log(logging.INFO, 'Last accessed Locality: ' + a)


if __name__ == '__main__':
    get_state_addresses('1')
    get_state_addresses('2')
    get_state_addresses('3')
    get_state_addresses('4')
    get_state_addresses('5')
    get_state_addresses('6')
    get_state_addresses('7')
    get_state_addresses('8')
    get_state_addresses('9')
    run_addresses('addresses_state_1.txt', '1', 1)
    run_addresses('addresses_state_2.txt', '2', 1)
    run_addresses('addresses_state_3.txt', '3', 1)
    run_addresses('addresses_state_4.txt', '4', 1)
    run_addresses('addresses_state_5.txt', '5', 1)
    run_addresses('addresses_state_6.txt', '6', 1)
    run_addresses('addresses_state_7.txt', '7', 1)
    run_addresses('addresses_state_8.txt', '8', 1)
    run_addresses('addresses_state_9.txt', '9', 1)
    get_state_localities('1')
    get_state_localities('2')
    get_state_localities('3')
    get_state_localities('4')
    get_state_localities('5')
    get_state_localities('6')
    get_state_localities('7')
    get_state_localities('8')
    get_state_localities('9')
    run_localities('localities_state_1.txt', '1', 1)
    run_localities('localities_state_2.txt', '2', 1)
    run_localities('localities_state_3.txt', '3', 1)
    run_localities('localities_state_4.txt', '4', 1)
    run_localities('localities_state_5.txt', '5', 1)
    run_localities('localities_state_6.txt', '6', 1)
    run_localities('localities_state_7.txt', '7', 1)
    run_localities('localities_state_8.txt', '8', 1)
    run_localities('localities_state_9.txt', '9', 1)
