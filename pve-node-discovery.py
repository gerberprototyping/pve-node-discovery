#!/usr/bin/env python3
from flask import Flask, request, make_response
from markupsafe import escape

import traceback
import argparse
import requests
import json
import os


METRICS_PORT = 9951


app = Flask(__name__)



def findMetricByID(id:str, metrics:json) -> json:
    for metric in metrics:
        if metric["metric"]["id"] == id:
            return metric


def getGuests(prometheus:str) -> json:
    response = requests.get(
        prometheus+'/api/v1/query',
        params={'query': 'pve_guest_info'}
    )
    pve_guest_info = response.json()['data']['result']
    response = requests.get(
        prometheus+'/api/v1/query',
        params={'query': 'pve_up'}
    )
    pve_up = response.json()['data']['result']
    guests = []
    for guest in pve_guest_info:
        id = guest['metric']['id']
        if '0' != findMetricByID(id, pve_up)['value'][1]:
            guests.append(guest['metric'])
    return guests


def initArgParse():
    parser = argparse.ArgumentParser(description='This microservice is intended'
            +'to allow for auto-discovery of Prometheus Node Exporters runningon Proxmox VE guests')
    parser.add_argument('--listen-host', dest='listen_host')
    parser.add_argument('--listen-port', dest='listen_port')
    parser.add_argument('--prometheus-url', dest='prometheus_url')
    parser.add_argument('--guest-domain', dest='guest_domain')
    parser.add_argument('--guest-port', dest='guest_port')
    parser.add_argument('--exclude', dest='exclude', action='append')
    parser.add_argument('--map-from', dest='map_from', action='append')
    parser.add_argument('--map-to', dest='map_to', action='append')
    return parser


PARAMS = {}
def parseParams(parser):
    args = parser.parse_args()
    # Prase listen-host
    if args.listen_host:
        PARAMS['listen-host'] = args.listen_host
    elif os.environ.get('NODE_DISCOVERY_LISTEN_HOST'):
        PARAMS['listen-host'] = os.environ.get('NODE_DISCOVERY_LISTEN_HOST')
    else:
        PARAMS['listen-host'] = '0.0.0.0'
    print('PARAM listen-host = %s'%PARAMS['listen-host'])
    # Parse listen-port
    if args.listen_port:
        PARAMS['listen-port'] = args.listen_port
    elif os.environ.get('NODE_DISCOVERY_LISTEN_PORT'):
        PARAMS['listen-port'] = os.environ.get('NODE_DISCOVER_LISTEN_PORT')
    else:
        PARAMS['listen-port'] = '9951'
    print('PARAM listen-port = %s'%PARAMS['listen-port'])
    # Parse prometheus-url
    if args.prometheus_url:
        PARAMS['prometheus-url'] = args.prometheus_url
    elif os.environ.get('NODE_DISCOVERY_PROMETHEUS_URL'):
        PARAMS['prometheus-url'] = os.environ.get('NODE_DISCOVERY_PROMETHEUS_URL')
    else:
        raise ValueError('Parameter prometheus-url must not be empty')
    print('PARAM prometheus-url = %s'%PARAMS['prometheus-url'])
    # Parse guest-domain
    if args.guest_domain:
        PARAMS['guest-domain'] = '.'+args.guest_domain
    elif os.environ.get('NODE_DISCOVERY_GUEST_DOMAIN'):
        PARAMS['guest-domain'] = '.'+os.eviron.get('NODE_DISCOVERY_GUEST_DOMAIN')
    else:
        PARAMS['guest-domain'] = ''
    print('PARAM guest-domain = %s'%PARAMS['guest-domain'])
    # Parse guest-port
    if args.guest_port:
        PARAMS['guest-port'] = '.'+args.guest_port
    elif os.environ.get('NODE_DISCOVERY_GUEST_PORT'):
        PARAMS['guest-port'] = '.'+os.eviron.get('NODE_DISCOVERY_GUEST_PORT')
    else:
        PARAMS['guest-port'] = '9100'
    print('PARAM guest-port = %s'%PARAMS['guest-port'])
    # Parse exclude
    if args.exclude:
        PARAMS['exclude'] = args.exclude
    elif os.environ.get('NODE_DISCOVERY_EXCLUDE'):
        PARAMS['exclude'] = os.environ.get('NODE_DISCOVERY_EXCLUDE').split(',')
    else:
        PARAMS['exclude'] = []
    print('PARAM exclude = %s'%PARAMS['exclude'])
    # Parse map-from
    if args.map_from:
        PARAMS['map-from'] = args.map_from
    elif os.environ.get('NODE_DISCOVERY_MAP_FROM'):
        PARAMS['map-from'] = os.environ.get('NODE_DISCOVERY_MAP_FROM').split(',')
    else:
        PARAMS['map-from'] = []
    # Parse map-to
    if args.map_to:
        PARAMS['map-to'] = args.map_to
    elif os.environ.get('NODE_DISCOVERY_MAP_TO'):
        PARAMS['map-to'] = os.environ.get('NODE_DISCOVERY_MAP_TO').split(',')
    else:
        PARAMS['map-to'] = []
    if len(PARAMS['map-from']) != len(PARAMS['map-to']):
        raise ValueError('Parameters map-from and map-to must be given in pairs')
    for i in range(len(PARAMS['map-from'])):
        print('PARAM mapping = %s -> %s'%(PARAMS['map-from'][i],PARAMS['map-to'][i]))


@app.route('/')
def webroot():
    try:
        static_configs = []
        for guest in getGuests(PARAMS['prometheus-url']):
            if not guest['name'] in PARAMS['exclude']:
                dns_name = guest['name']
                if guest['name'] in PARAMS['map-from']:
                    index = PARAMS['map-from'].index(guest['name'])
                    dns_name = PARAMS['map-to'][index]
                targets = [
                    dns_name+PARAMS['guest-domain']+':'+PARAMS['guest-port']
                ]
                labels = {
                    'pve_id': guest['id'],
                    'pve_instance': guest['instance'],
                    'pve_job': guest['job'],
                    'name': guest['name'],
                    'pve_node': guest['node'],
                    'pve_type': guest['type'],
                }
                static_configs.append({
                    'targets': targets,
                    'labels': labels,
                })
        response = make_response(json.dumps(static_configs), 200)
        response.mimetype = 'application/json'
        return response
    except Exception:
        traceback.print_exc()
        return make_response('<p>Internal error occured. See server logs.</p>', 500)

@app.route('/static-configs')
def metrics():
    return webroot()

@app.route('/healthz')
def health():
    response = make_response('OK', 200)
    response.mimetype = 'text/plain'
    return response




if __name__ == '__main__':
    parser = initArgParse()
    parseParams(parser)
    app.run(host=PARAMS['listen-host'],port=PARAMS['listen-port'])
