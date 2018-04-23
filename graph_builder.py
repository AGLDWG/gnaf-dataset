import logging
import _config as config
import model.address


def get_state_addresses(state_pid):
    cursor = config.get_db_cursor()
    s = '''SELECT address_detail_pid 
        FROM gnaf.address_detail 
        WHERE locality_pid 
        IN (SELECT locality_pid FROM gnaf.locality WHERE state_pid = '{}') 
        ORDER BY address_detail_pid;'''.format(state_pid)
    cursor.execute(s)

    with open('addresses_state_{}.txt'.format(state_pid), 'w') as f:
        for row in cursor.fetchall():
            r = config.reg(cursor, row)
            f.write(str(r.address_detail_pid) + '\n')


def run(index_file, data_file_count):
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

    data_file_stem = 'data-'
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
                    model.address.AddressRenderer(a, focus=True, db_cursor=cursor)
                        .export_rdf(view='gnaf', format='text/n3').decode('utf-8')
                )
        except Exception as e:
            logging.log(logging.DEBUG, 'address ' + a, e)
            print('address ' + a + '\n')
            print(e)
            with open('faulty.log', 'a') as f:
                f.write(addr + '\n')
        finally:
            logging.log(logging.INFO, 'Last accessed Address: ' + a)


if __name__ == '__main__':
    run('addresses_state_8.txt', '1')
    # get_state_addresses('1')
    # get_state_addresses('2')
    # get_state_addresses('3')
    # get_state_addresses('4')
    # get_state_addresses('5')
    # get_state_addresses('6')
    # get_state_addresses('7')
    # get_state_addresses('8')
    # get_state_addresses('9')
