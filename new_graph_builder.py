#!/usr/bin/env python3
#
import logging
import os
import sys
import pickle
from threading import Thread
import rdflib
import pyldapi
from pyldapi.exceptions import RegOfRegTtlError
from model import NotFoundError
from app import app

# --- CONFIGURABLE OPTIONS
HARVESTABLE_INSTANCE_VIEW = "gnaf"
MULTI_PROCESSING = True
MULTI_THREADING = True
USE_SAVED_REGISTER_INDEX = True
#TODO: Automate this, somehow.
INSTANCE_URI_TO_LOCAL_ROUTE = {
    "http://linked.data.gov.au/dataset/gnaf/locality/": "/locality/",
    "http://linked.data.gov.au/dataset/gnaf/address/": "/address/",
    "http://linked.data.gov.au/dataset/gnaf/streetLocality/": "/streetLocality/",
    "http://linked.data.gov.au/dataset/gnaf/addressSite/": "/addressSite/",
}


# -- END CONFIGURABLE OPTIONS
# ---------------------------

APP_ROFR = list()  # uri, rule, endpoint_func
APP_REGISTERS = list()  # uri, rule, endpoint_func

if MULTI_PROCESSING:
    from multiprocessing import Process as m_Worker
elif MULTI_THREADING:
    m_Worker = Thread
else:
    m_Worker = None


def request_register_query(uri, page=1, per_page=500):
    for _i in APP_REGISTERS:
        (r_uri, r_rule, r_endpoint_func) = _i
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
        with open("./instance/{}_p{}_s{}.nt".format(reg_uri_to_filename(reg_uri), str(worker_index), str(iig)),
                  'ab+') as inst_file:
            for inst in instance_s_group:
                local_instance_url = str(inst).replace(replace_s, replace_r)
                m = endpoint_rule.match("|" + local_instance_url)

                dummy_request_uri = "http://localhost:5000" + local_instance_url + \
                                    "?_view={:s}&_format=application/n-triples".format(HARVESTABLE_INSTANCE_VIEW)
                test_context = app.test_request_context(dummy_request_uri)
                try:
                    if len(m) < 1:
                        with test_context:
                            resp = endpoint_func()
                    else:
                        with test_context:
                            resp = endpoint_func(**m)
                except NotFoundError:
                    with open("{}_not_found.txt".format(reg_uri_to_filename(reg_uri)), 'a+') as nf:
                        nf.write("{}\n".format(dummy_request_uri))
                    continue
                except Exception as e:
                    import traceback
                    with open("{}_error.txt".format(reg_uri_to_filename(reg_uri)), 'a+') as nf:
                        nf.write("{}\n".format(dummy_request_uri))
                        nf.write("{}\n".format(repr(e)))
                        traceback.print_tb(e.__traceback__, file=nf)
                        nf.write('\n')
                    traceback.print_tb(e.__traceback__)  #to stderr
                    continue
                if isinstance(resp, pyldapi.Renderer):
                    resp.format = "application/n-triples"
                    resp = resp.render()
                if hasattr(resp, 'status_code') and hasattr(resp, 'data'):
                    assert resp.status_code == 200
                    if isinstance(resp.data, bytes):
                        data = resp.data
                    elif isinstance(resp.data, str):
                        data = resp.data.encode(encoding='utf-8')
                    else:
                        raise RuntimeError("response.data in the wrong format.")
                    inst_file.write(data)
                elif isinstance(resp, rdflib.Graph):
                    g = resp
                    g.serialize(destination=inst_file, format="nt")
    return True


def harvest_register(reg_uri):
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
                new_instances = request_register_query(reg_uri, page=page, per_page=10000)
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
    os.makedirs("./instance", exist_ok=True)
    if MULTI_THREADING:
        INSTANCE_PARALLEL = 8  # Running 8 threads in parallel
        n_instances = len(instances)
        extra = 1 if (n_instances % INSTANCE_PARALLEL) > 0 else 0
        # Each parallel thread gets total_instances / threads.
        # if there is remainder, give each thread one more.
        instance_groups = list(grouper(instances, (n_instances//INSTANCE_PARALLEL)+extra))
        t_workers = []
        for iig, instance_group in enumerate(instance_groups):
            _worker = Thread(target=_harvest_register_worker_fn, args=(iig, reg_uri, instance_group),
                               kwargs={'serial_chunk_size':1000, 'endpoint_func':endpoint_func, 'endpoint_rule':endpoint_rule, 'replace_s': replace_s, 'replace_r': replace_r})
            _worker.start()
            t_workers.append(_worker)
        results = [_w.join() for _w in t_workers]
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

