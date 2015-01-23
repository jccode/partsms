# -*- coding: utf-8 -*-

import logging, logging.config
import urllib2, base64, pdb, traceback
import os, os.path
import sys
import codecs
import json

# variables
DATA_DIR = os.path.join( os.path.expanduser("~"), "temp", "sputterparts" )
ARCHIVE_DIR = os.path.join( DATA_DIR, "archive" )

# log
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('SputterPartsMS Client')


def demo():
    json_data = '{"request_no": "A201404001024", "apply_type": "app_type", "material_type": "mtype", "apply_reason": "aReason", "employee": "9527", "cost_center": "34E110", "approver": "[\\"9527\\", \\"9529\\"]", "request_date": "2014-08-27T12:30:00.000Z", "requestdetail_set": [{"pn": "110290", "bin": "L5A201", "description": "Gasket Retainer Ass", "qty": 10, "actual_qty": null, "unit": "pcs", "over_plan_usage": null, "balance": "100", "usage_by_once": null, "remark": ""}, {"pn": "110291", "bin": "E5B401", "description": "Gasket Retainer Ass", "qty": 5, "actual_qty": null, "unit": "pcs", "over_plan_usage": null, "balance": "50", "usage_by_once": null, "remark": ""}]}'
    url = 'http://127.0.0.1:8000/api/partsrequest/'
    req = urllib2.Request(url, data = json_data, headers = {'Content-Type':'application/json'})
    username = 'bohu.tang'
    password = 'bohu.tang'
    cridential = base64.encodestring('%s:%s' % (username, password))[:-1]
    auth_header = "Basic %s" % cridential
    req.add_header("Authorization", auth_header)
    try:
        handle = urllib2.urlopen(req)
        resp = handle.read()
        handle.close()
    except IOError as e:
        if hasattr(e, 'code'):
            if e.code != 401:
                print 'We got another error'
                print e.code
                print e
            else:
                print e.headers
                print e.headers['www-authenticate']


def call_partsms_api(data):
    """
    call partms api to insert data
    
    Arguments:
    - `data`:
    """
    logger.info("Calling partsms api service to insert data")
    url = 'http://127.0.0.1:8000/api/partsrequest/'
    req = urllib2.Request(url, data = data, headers = {'Content-Type':'application/json'})
    username = 'notesapi'
    password = 'notesapi'
    cridential = base64.encodestring('%s:%s' % (username, password))[:-1]
    auth_header = "Basic %s" % cridential
    req.add_header("Authorization", auth_header)
    try:
        handle = urllib2.urlopen(req)
        resp = handle.read()
        handle.close()
        return True
    except IOError as e:
        logger.error("Some error occured when invoking partsms api. As belows:")
        logger.error("----------------------------------------")
        logger.error(e.read())
        logger.error("----------------------------------------")
        # if hasattr(e, 'code'):
        #     if e.code == 403:
        #         logger.error("The authorization of the invocation is error.")
        #     elif e.code == 400:
        #         logger.error("Data error when invoking the service")
        #         print e.__dict__
        #     else:
        #         pass
        logger.exception(e)
        return False


def make_archive_dir_if_necessary():
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)


def process_data_files():
    datafiles = [ f for f in os.listdir(DATA_DIR) if os.path.isfile(os.path.join(DATA_DIR, f)) ]
    for datafile in datafiles:
        logger.info("Loading data file %s" % datafile)
        # require data file with utf-8 encoding
        with open(os.path.join(DATA_DIR, datafile), "r") as f: 
        # with codecs.open(os.path.join(DATA_DIR, datafile), "r", "gb2312") as f:
            # json = f.read()
            try:
                data = json.load(f)
                if type(data) is list:
                    for el in data:
                        call_partsms_api(json.dumps(el))
                        # archive
                else:
                    call_partsms_api(json.dumps(data))
                    # archive
            except ValueError as e:
                logger.error("Data file is not a valid json file")
                logger.exception(e)
            except Exception as e:
                logger.error("Loading data file failed")
                logger.exception(e)


def main():
    logger.info("Sputter Partsms client start process data files.")
    make_archive_dir_if_necessary()
    process_data_files()
    logger.info("All files have been processed.")


if __name__ == '__main__':
    main()
