import logging

from psycopg2 import sql

import _config as config
from db import get_db_cursor, reg
import model.address
import model.locality
import threading
from queue import Queue

from model import NotFoundError

dbschema=sql.Identifier(config.DB_SCHEMA)

def line_count(filename):
    lines = 0
    buf_size = 1024 * 1024
    with open(filename) as f:
        read_f = f.read  # loop optimization
        buf = read_f(buf_size)
        while buf:
            lines += buf.count('\n')
            buf = read_f(buf_size)
    return lines

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


def run_addresses(index_file, file_id, data_file_count, threaded=False):
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

    if threaded:
        return run_addresses_threaded(index_file, file_id, data_file_count, threaded)

    lines = line_count(index_file)

    with get_db_cursor() as cursor:
        data_file_stem = 'data-address-'+str(file_id)+"-"
        # for idx, addr in enumerate(cursor.fetchall()):
        for idx, addr in enumerate(open(index_file, 'r').readlines()):
            print("Getting Address {} of {}".format(idx+1, lines))
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


def run_addresses_threaded(index_file, file_id, data_file_count, threads=8):
    logging.basicConfig(filename='graph_builder.log',
                        level=logging.DEBUG,
                        datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s %(message)s')

    '''
    - For each Address in the Address Register,
    - Create an Address class instance using the ID
    - Serialise that to a file
    '''
    DATA_FILE_LENGTH_MAX = 1000
    if threads is True:
        threads = 8
    elif threads == 1 or threads == 0 or threads is False:
        return run_addresses(index_file, file_id, data_file_count)

    lines = line_count(index_file)

    try:
        threads = int(threads)
    except ValueError:
        threads = 8
    input_queue = Queue(maxsize=threads*2)
    output_queue = Queue(maxsize=threads*2)
    eof_token = object()

    def _input_thread_processor(args):
        nonlocal input_queue
        nonlocal output_queue
        nonlocal lines
        nonlocal eof_token
        nonlocal file_id

        t = args
        with get_db_cursor() as cursor:
            while True:
                next_item = input_queue.get()
                if next_item is eof_token:
                    break
                i, _a = next_item
                print("[T{}] Getting Address {} of {}.".format(t, i+1, lines))
                new_triples = None
                try:
                    new_triples = model.address.Address(_a, focus=True, db_cursor=cursor) \
                        .export_rdf(view='gnaf').serialize(format='nt').decode('utf-8')
                except NotFoundError as e1:
                    msg = "address {} not found.".format(a)
                    logging.warning(msg)
                    print(msg)
                    with open('not_found_{}.log'.format(file_id), 'a') as _f:
                        _f.write(a + '\n')
                except Exception as e:
                    logging.log(logging.DEBUG, 'address ' + a, e)
                    print('address ' + a + '\n')
                    print(e)
                    with open('faulty_{}.log'.format(file_id), 'a') as _f:
                        _f.write(a + '\n')
                if new_triples is not None:
                    output_queue.put(new_triples)
        print("[T{}] Thread terminated.".format(t))

    data_file_stem = 'data-address-' + str(file_id) + "-"

    def _output_thread_processor():
        nonlocal data_file_count
        nonlocal output_queue
        nonlocal eof_token
        nonlocal data_file_stem
        last_data_file_count = data_file_count
        fo = None
        try:
            while True:
                if last_data_file_count != data_file_count:
                    if fo:
                        fo.close()
                        fo = None
                new_triples = output_queue.get()
                if new_triples is eof_token:
                    break
                else:
                    if fo is None:
                        fo = open(data_file_stem + str(data_file_count).zfill(4) + '.nt', 'a')
                        last_data_file_count = data_file_count
                    fo.write(new_triples)
                    fo.flush()
        finally:
            if fo:
                fo.close()
        print("[T-o] Thread terminated.")

    my_input_threads = [threading.Thread(target=_input_thread_processor, args=(_i,)) for _i in range(threads)]
    _ = [_t.start() for _t in my_input_threads]
    my_output_thread = threading.Thread(target=_output_thread_processor)
    my_output_thread.start()
    for idx, addr in enumerate(open(index_file, 'r').readlines()):
        a = addr.strip()
        try:
            # every DATA_FILE_LENGTH_MAXth URI, create a new destination file
            if (idx + 1) % DATA_FILE_LENGTH_MAX == 0:
                data_file_count += 1
            input_queue.put((idx, a))
        except Exception as e:
            logging.log(logging.DEBUG, 'address ' + a, e)
            print('address ' + a + '\n')
            print(e)
            with open('faulty.log', 'a') as f:
                f.write(addr + '\n')
        finally:
            logging.log(logging.INFO, 'Last accessed Address: ' + a)
    _ = [input_queue.put(eof_token) for _t in my_input_threads]
    _ = [_t.join() for _t in my_input_threads]
    output_queue.put(eof_token)
    my_output_thread.join()


def run_localities(locality_index_file, file_id, data_file_count, threaded=False):
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
                    fl.write(rdf)
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
