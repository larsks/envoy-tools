#!/usr/bin/env python

import sys
import argparse
import base64

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
        bottle.post('/emu_reports/performance_report')(self.performance_report)
        bottle.post('/emu_reports/task_complete')(self.task_complete)

    def log_response(self, body):
        tf = tempfile.NamedTemporaryFile(
            dir=self.config.spool_dir,
            delete=False,
            prefix=time.strftime('%Y-%m-%dT%H:%M:%S-', time.localtime(time.time())),
            suffix='.response')

        for k,v in bottle.response.headers.items():
            print >>tf, '%s = %s' % (k,v)
        print >>tf

        if 'text/' in bottle.response.headers['content-type']:
            tf.write(body)
        elif 'application/xml' in bottle.response.headers['content-type']:
            tf.write(body)
        elif 'application/x-deflate' in bottle.response.headers['content-type']:
            tf.write(zlib.decompress(body))
        else:
            tf.write(base64.encodestring(body))

        return body

    def log_request(self):
        tf = tempfile.NamedTemporaryFile(
            dir=self.config.spool_dir,
            delete=False,
            prefix=time.strftime('%Y-%m-%dT%H:%M:%S-', time.localtime(time.time())),
            suffix='.request')

        print >>tf, bottle.request.method, bottle.request.url
        print >>tf
        for k,v in bottle.request.headers.items():
            print >>tf, '%s = %s' % (k,v)
        print >>tf

        if 'text/' in bottle.request.headers['content-type']:
            tf.write(bottle.request.body.read())
        elif 'application/xml' in bottle.request.headers['content-type']:
            tf.write(bottle.request.body.read())
        elif 'application/x-deflate' in bottle.request.headers['content-type']:
            tf.write(zlib.decompress(bottle.request.body.read()))
        else:
            tf.write(base64.encodestring(bottle.request.body.read()))
        bottle.request.body.seek(0)

    def task_complete(self):
        self.log_request()

        proxyreq = urllib2.Request(
            '%s/task_complete?%s' % (
            self.config.upstream_url,
        bottle.request.query_string),
            bottle.request.body.read(),
            {'Content-type': bottle.request.headers['content-type']})

        fd = urllib2.urlopen(proxyreq)

        bottle.response.status = fd.getcode()
        bottle.response.set_header('Content-type', fd.headers['content-type'])
        return self.log_response(fd.read())

    def performance_report(self):
        self.log_request()

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
            prefix=time.strftime('%Y-%m-%dT%H:%M:%S-', time.localtime(time.time())),
            suffix='.xml')
        tf.write(urllib.unquote(parsed_data['body']))

        # Send request on to server.
        bottle.request.body.seek(0)
        proxyreq = urllib2.Request(
            '%s/performance_report?%s' % (
            self.config.upstream_url,
        bottle.request.query_string),
            bottle.request.body.read(),
            {'Content-type': 'application/x-deflate'})

        fd = urllib2.urlopen(proxyreq)

        bottle.response.status = fd.getcode()
        bottle.response.set_header('Content-type', fd.headers['content-type'])
        return self.log_response(fd.read())

def parse_args():
    p = argparse.ArgumentParser(description='Envoy data proxy')

    p.add_argument('--bind-address', '-b', default='127.0.0.1')
    p.add_argument('--port', '-p', default='8080')
    p.add_argument('--upstream-url', '-U',
        default='https://reports.enphaseenergy.com/emu_reports')
    p.add_argument('--spool-dir', '-s',
        default='/var/spool/envoy')

    return p.parse_args()

def main():
    args = parse_args()
    app = Proxy(args)

    bottle.run(host=args.bind_address, port=args.port)

if __name__ == '__main__':
    main()

