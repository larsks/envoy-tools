========================
Envoy intercepting proxy
========================

This tool is designed to intercept the data posted by the Enphase
Envoy to the Enphase servers.  It writes data to a local spool
directory and then sends it on to the Enphase servers.

Requirements
============

The proxy web application requires a recent version of the bottle_ web framework.

.. _bottle: http://bottlepy.org/

Configuration
=============

Stunnel
-------

We will use stunnel to intercept the accept the https connection and
proxy it to our web application, which expects plain http.  You will
need the following stunnel configuration::

  [https_in]
  accept = 4430
  cert = /etc/pki/tls/certs/localhost.crt
  connect = 127.0.0.1:8080

iptables
--------

You will need to set up an iptables ``REDIRECT`` rule in order to
intercept the outbound connections::

  iptables -t nat -A PREROUTING -s <your_envoy_address> \
    -p tcp --dport 443 -j REDIRECT --to-ports 4430

This will accept packets from your Envoy to port 443 and redirect them
to port 4430.


