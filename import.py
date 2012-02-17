#!/usr/bin/python

import os
import sys
import optparse
from lxml import etree

import model

def parse_args():
    p = optparse.OptionParser()
    p.add_option('--dburi', default='sqlite:///envoy.db')
    p.add_option('--debug', action='store_true')
    return p.parse_args()

def main():
    opts, args = parse_args()

    print 'Using database: %s' % (opts.dburi)

    session = model.init(opts.dburi, echo=opts.debug)

    for datafile in args:
        data = etree.parse(open(datafile))

        node_report = data.getroot()
        report = session.query(model.Report).get(
                node_report.get('report_timestamp'))

        if report:
            continue

        report = model.Report(report_timestamp =
                node_report.get('report_timestamp'))

        node_envoy = node_report.find('envoy')

        envoy = session.query(model.Envoy).get(node_envoy.get('serial_num'))
        if not envoy:
            envoy = model.Envoy(ip_addr = node_envoy.get('ip_addr'),
                    mac_addr = node_envoy.get('mac_addr'),
                    timezone = node_envoy.get('timezone'),
                    serial_num = node_envoy.get('serial_num'))

            session.add(envoy)

	envoy.sw_version = node_envoy.get('sw_version')

        for node_device in node_report.findall('device'):
            device = session.query(model.Device).get(node_device.get('eqid'))
            if not device:
                device = model.Device(eqid = node_device.get('eqid'),
                        part_num=node_device.get('part_num'),
                        device_type=node_device.get('device_type'),
                        envoy=envoy)
                session.add(device)

            device.image_bits = node_device.get('image_bits')
            device.admin_state = node_device.get('admin_state')
            device.condition_flags = node_device.get('condition_flags')
            device.observed_flags = node_device.get('observed_flags')
            device.control_bits = node_device.get('control_bits')

        for node_interval in node_report.findall('interval'):
            interval = session.query(model.Interval).get(
                    node_interval.get('id'))
            if interval:
                continue

            interval = model.Interval(
                    report=report,
                    id=node_interval.get('id'),
                    stat_duration=node_interval.get('stat_duration'),
                    interval_duration=node_interval.get('interval_duration'),
                    eqid=node_interval.get('eqid'),
                    end_date=node_interval.get('end_date'))

            stats = model.IntervalStats(
                    interval=interval)

            for i,v in enumerate(node_interval.get('stats').split(',')):
                setattr(stats, 'val%d' % i, v)

            session.add(stats)
            session.add(interval)

        for node_event in node_report.findall('event'):
            event = session.query(model.Event).get(
                    node_event.get('id'))
            if event:
                continue

            event = model.Event(
                    id = node_event.get('id'),
                    correlation_id = node_event.get('correlation_id'),
                    event_state = node_event.get('event_state'),
                    event_code = node_event.get('event_code'),
                    eqid = node_event.get('eqid'),
                    serial_num = node_event.get('serial_num'),
                    event_date = node_event.get('event_date'),
                    )

            device = session.query(model.Device).get(event.serial_num)
            if device:
                device.events.append(event)
            report.events.append(event)

            session.add(event)

        envoy.reports.append(report)
        session.add(report)
        session.commit()

if __name__ == '__main__':
    main()


