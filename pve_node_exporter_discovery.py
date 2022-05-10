#!/usr/bin/env python3
import xml.etree.ElementTree as ETree
import socket, time

from flask import Flask, request, make_response
from markupsafe import escape
import requests, json


METRICS_PORT = 24684


app = Flask(__name__)



def findMetricByID(id:str, metrics:json) -> json:
    for metric in metrics:
        if metric["metric"]["id"] == id:
            return metric


def getGuests(prometheus:str):
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
            guests.append(guest['metric']['name'])
    return guests


@app.route('/')
def webroot():
    try:
        prometheus = escape(request.args.get('prometheus','https://prometheus'))
        body = [{'targets': getGuests(prometheus)}]
        response = make_response(json.dumps(body), 200)
        response.mimetype = 'application/json'
        return response
    except Exception as ex:
        print(ex)
        return make_response('<p>Bad Request</p>', 404)

@app.route('/metrics')
def metrics():
    return webroot()

@app.route('/healthz')
def health():
    response = make_response('OK', 200)
    response.mimetype = 'text/plain'
    return response




if __name__ == '__main__':
    app.run(host='0.0.0.0',port=METRICS_PORT)
