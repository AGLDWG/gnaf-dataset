import logging
import _config as config
from psycopg2 import sql
import model.address


if __name__ == '__main__':
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
    #  s = sql.SQL('SELECT address_detail_pid FROM gnaf.address_detail ORDER BY address_detail_pid;')
    s = sql.SQL(
        'SELECT address_detail_pid '
        'FROM gnaf.address_detail '
        'WHERE address_detail_pid >= \'GANSW704750163\' '
        'ORDER BY address_detail_pid;')
    cursor.execute(s)

    data_file_stem = 'data-'
    data_file_count = 1
    for idx, addr in enumerate(cursor.fetchall()):
        try:
            # record the Address being processed in case of failure
            # every DATA_FILE_LENGTH_MAXth URI, create a new destination file
            if (idx + 1) % DATA_FILE_LENGTH_MAX == 0:
                data_file_count += 1
            with open(data_file_stem + str(data_file_count).zfill(4) + '.nt', 'a') as fl:
                fl.write(
                    model.address.AddressRenderer(addr[0], focus=True, db_cursor=cursor)
                        .export_rdf(view='gnaf', format='text/n3').decode('utf-8')
                )
        except Exception as e:
            logging.log(logging.DEBUG, e)
            print(e)
        finally:
            logging.log(logging.INFO, 'Last accessed Address: ' + addr[0])
