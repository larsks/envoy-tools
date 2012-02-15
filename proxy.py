#!/usr/bin/env python

import sys
import argparse

import zlib
import urllib
import urllib2
import time

import tempfile
import bottle

class Proxy(object):
    def __init__(self, config):
        self.config = config
        self.setup_routes()

    def setup_routes(self):
        bottle.post('/emu_reports/performance_report')(self.report)

    def report(self):
        if not bottle.request.headers['content-type'] == 'application/x-deflate':
            raise bottle.HTTPError(code=500,
                output='Unsupport content type.')
        
        raw_data = zlib.decompress(bottle.request.body.read())
        parsed_data = dict([x.split('=', 1) for x in raw_data.split('&')])
        if not 'body' in parsed_data:
            raise bottle.HTTPError(code=500,
                output='Missing required field "body" in request.')

        tf = tempfile.NamedTemporaryFile(
            dir=self.config.spool_dir,
            delete=False,
            prefix=time.strftime('%Y-%m-%dT%H:%M:%S-', time.localtime(time.time())))
        tf.write(urllib.unquote(parsed_data['body']))

        # Send request on to server.
        bottle.request.body.seek(0)
        proxyreq = urllib2.Request(self.config.upstream_url,
            bottle.request.body.read(),
            {'Content-type': 'application/x-deflate'})

        fd = urllib2.urlopen(proxyreq)

        bottle.response.status = fd.getcode()
        bottle.response.set_header('Content-type', fd.headers['content-type'])
        return fd.read()

def parse_args():
    p = argparse.ArgumentParser(description='Envoy data proxy')

    p.add_argument('--bind-address', '-b', default='127.0.0.1')
    p.add_argument('--port', '-p', default='8080')
    p.add_argument('--upstream-url', '-U',
        default='https://reports.enphaseenergy.com/emu_reports/performance_report?webcomm_version=3.0')
    p.add_argument('--spool-dir', '-s',
        default='/var/spool/envoy')

    return p.parse_args()

def main():
    args = parse_args()
    app = Proxy(args)

    bottle.run(host=args.bind_address, port=args.port)

if __name__ == '__main__':
    main()

