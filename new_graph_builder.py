#!/usr/bin/env python3
#
import logging
import sys
import pickle

import rdflib
from psycopg2 import sql
import pyldapi
from pyldapi.exceptions import RegOfRegTtlError

import _config as config
from db import get_db_cursor, reg
import threading
from queue import Queue

from model import NotFoundError

dbschema=sql.Identifier(config.DB_SCHEMA)

from app import app

APP_ROFR = list() #uri, rule, endpoint_func
APP_REGISTERS = list() #uri, rule, endpoint_func
MULTI_PROCESSING = True
MULTI_THREADING = True
USE_SAVED_REGISTER_INDEX = True

from threading import Thread

if MULTI_PROCESSING:
    from multiprocessing import Process as m_Worker
elif MULTI_THREADING:
    m_Worker = Thread
else:
    m_Worker = None



#TODO: Automate this, somehow.
INSTANCE_URI_TO_LOCAL_ROUTE = {
    "http://linked.data.gov.au/dataset/gnaf/locality/": "/locality/",
    "http://linked.data.gov.au/dataset/gnaf/address/": "/address/",
    "http://linked.data.gov.au/dataset/gnaf/streetLocality/": "/streetLocality/",
    "http://linked.data.gov.au/dataset/gnaf/addressSite/": "/addressSite/",
}
HARVESTABLE_INSTANCE_VIEW = "gnaf"


def request_register_query(uri, page=1, per_page=500):
    for i in APP_REGISTERS:
        (r_uri, r_rule, r_endpoint_func) = i
        if r_uri == str(uri):
            break
    else:
        raise RuntimeError("App does not have endpoint for uri: {}".format(uri))
    dummy_request_uri = "http://localhost:5000" + str(r_rule) +\
                     "?_view=reg&_format=_internal&per_page={}&page={}".format(per_page, page)
    test_context = app.test_request_context(dummy_request_uri)
    with test_context:
        resp = r_endpoint_func()

    try:
        return resp.register_items
    except AttributeError:
        raise NotFoundError()

def find_app_registers():
    for rule in app.url_map.iter_rules():
        if '<' not in str(rule):  # no registers can have a Flask variable in their path
            # make the register view URI for each possible register
            try:
                endpoint_func = app.view_functions[rule.endpoint]
            except (AttributeError, KeyError):
                continue
            try:
                dummy_request_uri = "http://localhost:5000" + str(rule) +\
                                    '?_view=reg&_format=_internal'
                test_context = app.test_request_context(dummy_request_uri)
                with test_context:
                    resp = endpoint_func()
                    if isinstance(resp, pyldapi.RegisterOfRegistersRenderer):
                        APP_ROFR.append((resp.uri, rule, endpoint_func))
                    elif isinstance(resp, pyldapi.RegisterRenderer):
                        APP_REGISTERS.append((resp.uri, rule, endpoint_func))
                    else:
                        pass
            except RegOfRegTtlError:  # usually an RofR renderer cannot find its rofr.ttl.
                raise Exception("Please generate rofr.ttl before running the graph_builder.")
            except Exception as e:
                raise e


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

def harvest_rofr():
    try:
        (r_uri, r_rule, r_endpoint_func) = APP_ROFR[0]
    except:
        raise RuntimeError("No RofR found in the App.")

    dummy_request_uri = "http://localhost:5000" + str(r_rule) +\
                     "?_view=reg&_format=_internal&per_page=500&page=1"
    test_context = app.test_request_context(dummy_request_uri)
    with test_context:
        resp = r_endpoint_func()
    if resp.register_items:
        registers = [r[0] for r in resp.register_items]
    else:
        raise NotImplementedError("TODO: Get registers directly from the returned graph.")
    return registers

def reg_uri_to_filename(reg_uri):
    return str(reg_uri).rstrip('/').replace("http://", "http_").replace("https://", "http_").replace("/","_").replace('#','')

def _harvest_register_worker_fn(worker_index, reg_uri, instances, serial_chunk_size=1000, **kwargs):
    endpoint_func = kwargs['endpoint_func']
    endpoint_rule = kwargs['endpoint_rule']
    replace_s = kwargs['replace_s']
    replace_r = kwargs['replace_r']
    n_instances = len(instances)
    assert n_instances > 0
    extra = 1 if (n_instances % serial_chunk_size) > 0 else 0
    serial_groups = list(grouper(instances, (n_instances // serial_chunk_size)+extra))
    for iig, instance_s_group in enumerate(serial_groups):
        for inst in instance_s_group:
            local_instance_url = str(inst).replace(replace_s, replace_r)
            m = endpoint_rule.match("|" + local_instance_url)

            dummy_request_uri = "http://localhost:5000" + local_instance_url + \
                                "?_view={:s}&_format=application/n-triples".format(HARVESTABLE_INSTANCE_VIEW)
            test_context = app.test_request_context(dummy_request_uri)
            if len(m) < 1:
                with test_context:
                    resp = endpoint_func()
            else:
                with test_context:
                    resp = endpoint_func(**m)
            if isinstance(resp, pyldapi.Renderer):
                resp.format = "application/n-triples"
                resp = resp.render()
            if hasattr(resp, 'status_code') and hasattr(resp, 'data'):
                assert resp.status_code == 200
                if isinstance(resp.data, bytes):
                    mode = 'ab+'
                elif isinstance(resp.data, str):
                    mode = 'a+'
                else:
                    raise RuntimeError("response.data in the wrong format.")
                with open("./instance/{}_{}_{}.nt".format(reg_uri_to_filename(reg_uri), str(worker_index), str(iig)),
                          mode) as inst_file:
                    inst_file.write(resp.data)
            elif isinstance(resp, rdflib.Graph):
                g = resp
                with open("./instance/{}_{}_{}.nt".format(reg_uri_to_filename(reg_uri), str(worker_index), str(iig)),
                          'ab+') as inst_file:
                    g.serialize(destination=inst_file, format="nt")
    return True

def harvest_register(reg_uri):
    if MULTI_PROCESSING:
        # make sure our pid can get a DB connection
        with get_db_cursor() as cur:
            print("Got cursor for our process, {}".format(id(cur)))
    instances = []
    print("got here with reg_uri {}".format(reg_uri))
    if USE_SAVED_REGISTER_INDEX:
        try:
            with open("./index_{}.pickle".format(reg_uri_to_filename(reg_uri)), 'rb') as reg_pickle:
                instances = pickle.load(reg_pickle)
                save_register_index = False
        except FileNotFoundError:
            save_register_index = True
    else:
        save_register_index = False
    if (not USE_SAVED_REGISTER_INDEX) or save_register_index:
        page = 1
        while True:
            try:
                new_instances = request_register_query(reg_uri, page=page, per_page=1000)
                assert len(new_instances) > 0
                instances.extend([i[0] for i in new_instances])
                page += 1
            except (NotFoundError, AssertionError) as e:
                print(e)
                break
        if len(instances) > 0 and save_register_index:
            with open("./index_{}.pickle".format(reg_uri_to_filename(reg_uri)), 'wb') as reg_pickle:
                pickle.dump(instances, reg_pickle)
    if len(instances) < 1:
        raise RuntimeError("Got no instances from reg uri: {}".format(reg_uri))
    first_instance = instances[0]

    for k in INSTANCE_URI_TO_LOCAL_ROUTE.keys():
        if first_instance.startswith(k):
            replace_s = k
            replace_r = INSTANCE_URI_TO_LOCAL_ROUTE[k]
            break
    else:
        raise RuntimeError("Cannot find a local route for that URI.")
    first_local_instance_url = str(first_instance).replace(replace_s, replace_r)
    for rule in app.url_map.iter_rules():
        m = rule.match("|"+first_local_instance_url)
        if m:
            endpoint_func = app.view_functions[rule.endpoint]
            endpoint_rule = rule
            break
    else:
        raise RuntimeError("No app rule matches that local route.")
    if MULTI_THREADING:
        INSTANCE_PARALLEL = 8
        n_instances = len(instances)
        extra = 1 if (n_instances % INSTANCE_PARALLEL) > 0 else 0
        instance_groups = list(grouper(instances, (n_instances//INSTANCE_PARALLEL)+extra))
        workers = []
        for iig, instance_group in enumerate(instance_groups):
            _worker = Thread(target=_harvest_register_worker_fn, args=(iig, reg_uri, instance_group),
                               kwargs={'serial_chunk_size':1000, 'endpoint_func':endpoint_func, 'endpoint_rule':endpoint_rule, 'replace_s': replace_s, 'replace_r': replace_r})
            _worker.start()
            workers.append(_worker)
        results = [_w.join() for _w in workers]
    else:
        results = []
        kwargs = {'serial_chunk_size': 1000, 'endpoint_func': endpoint_func, 'endpoint_rule': endpoint_rule,
                  'replace_s': replace_s, 'replace_r': replace_r}
        _r = _harvest_register_worker_fn(0, reg_uri, instances, **kwargs)
        results.append(_r)
    return results



##UTILS##
def grouper(iterable, n):
    assert is_iterable(iterable)
    if isinstance(iterable, (list, tuple)):
        return list_grouper(iterable, n)
    elif isinstance(iterable, (set, frozenset)):
        return set_grouper(iterable, n)

def list_grouper(iterable, n):
    assert isinstance(iterable, (list, tuple))
    assert n > 0
    iterable = iter(iterable)
    count = 0
    group = list()
    while True:
        try:
            group.append(next(iterable))
            count += 1
            if count % n == 0:
                yield tuple(group)
                group = list()
        except StopIteration:
            if len(group) < 1:
                raise StopIteration()
            else:
                yield tuple(group)
            break

def set_grouper(iterable, n):
    assert isinstance(iterable, (set, frozenset))
    assert n > 0
    iterable = iter(iterable)
    count = 0
    group = set()
    while True:
        try:
            group.add(next(iterable))
            count += 1
            if count % n == 0:
                yield frozenset(group)
                group = set()
        except StopIteration:
            if len(group) < 1:
                raise StopIteration()
            else:
                yield frozenset(group)
            break

def first(i):
    assert is_iterable(i)
    return next(iter(i))

def is_iterable(i):
    return isinstance(i, (list, set, tuple, frozenset))

if __name__ == '__main__':
    find_app_registers()
    if len(sys.argv) < 2:
        register = None
    else:
        register = sys.argv[1]
    if register is None:
        registers = harvest_rofr()
        if m_Worker:
            workers = []
            for i,r in enumerate(registers):
                t = m_Worker(target=harvest_register, args=(r,), name="worker"+str(i))
                t.start()
                workers.append(t)
            results = [_t.join() for _t in workers]
        else:
            results = []
            for r in registers:
                results.append(harvest_register(r))
    else:
        harvest_register(register)
    # get_state_addresses('1')
    # get_state_addresses('2')
    # get_state_addresses('3')
    # get_state_addresses('4')
    # get_state_addresses('5')
    #get_state_addresses('6')
    # get_state_addresses('7')
    # get_state_addresses('8')
    # get_state_addresses('9')
    # run_addresses('addresses_state_1.txt', '1', 1)
    # run_addresses('addresses_state_2.txt', '2', 1)
    # run_addresses('addresses_state_3.txt', '3', 1)
    # run_addresses('addresses_state_4.txt', '4', 1)
    # run_addresses('addresses_state_5.txt', '5', 1, True)
    #run_addresses('addresses_state_6.txt', '6', 1, 16)
    # run_addresses('addresses_state_7.txt', '7', 1)
    # run_addresses('addresses_state_8.txt', '8', 1)
    # run_addresses('addresses_state_9.txt', '9', 1)
    # get_state_localities('1')
    # get_state_localities('2')
    # get_state_localities('3')
    # get_state_localities('4')
    # get_state_localities('5')
    # get_state_localities('6')
    # get_state_localities('7')
    # get_state_localities('8')
    # get_state_localities('9')
    # run_localities('localities_state_1.txt', '1', 1)
    # run_localities('localities_state_2.txt', '2', 1)
    # run_localities('localities_state_3.txt', '3', 1)
    # run_localities('localities_state_4.txt', '4', 1)
    # run_localities('localities_state_5.txt', '5', 1)
    # run_localities('localities_state_6.txt', '6', 1)
    # run_localities('localities_state_7.txt', '7', 1)
    # run_localities('localities_state_8.txt', '8', 1)
    # run_localities('localities_state_9.txt', '9', 1)
