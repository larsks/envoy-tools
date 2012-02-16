from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine

Base = declarative_base()

class TableNameMixin (object):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

class Envoy (TableNameMixin,Base):
    serial_num = Column(String, primary_key=True)
    ip_addr = Column(String)
    mac_addr = Column(String)
    part_num = Column(String)
    timezone = Column(String)
    sw_version = Column(String)
    reports = relationship('Report', backref='envoy')
    devices = relationship('Device', backref='envoy')

class Report (TableNameMixin,Base):
    report_timestamp = Column(Integer, primary_key=True)
    envoy_id = Column(String, ForeignKey('envoy.serial_num'))
    intervals = relationship('Interval', backref='report')

class Device (TableNameMixin,Base):
    eqid = Column(String, primary_key=True)
    image_bits = Column(Integer)
    control_bits = Column(Integer)
    device_type = Column(Integer)
    admin_state = Column(Integer)
    condition_flags = Column(Integer)
    part_num = Column(String)
    events = relationship('Event', backref='device')
    envoy_id = Column(String, ForeignKey('envoy.serial_num'))

class Interval (TableNameMixin,Base):
    id = Column(Integer, primary_key=True)
    stat_duration = Column(Integer)
    interval_duration = Column(Integer)
    eqid = Column(String)
    end_date = Column(Integer)
    stats = relationship('IntervalStats', backref='interval')
    report_id = Column(Integer, ForeignKey('report.report_timestamp'))

class IntervalStats (TableNameMixin, Base):
    id = Column(Integer, primary_key=True)

    val0 = Column(Integer)
    val1 = Column(Integer)
    val2 = Column(Integer)
    val3 = Column(Integer)
    val4 = Column(Integer)
    val5 = Column(Integer)
    val6 = Column(Integer)
    val7 = Column(Integer)

    interval_id = Column(Integer, ForeignKey('interval.id'))

class Event (TableNameMixin,Base):
    id = Column(Integer, primary_key=True)

    correlation_id = Column(Integer)
    event_state = Column(Integer)
    event_code = Column(Integer)
    eqid = Column(Integer)
    serial_num = Column(Integer)
    event_date = Column(Integer)

    device_id = Column(Integer, ForeignKey('device.eqid'))

def init(dburi = 'sqlite:///:memory:', echo=False):
    engine = create_engine(dburi, echo=echo)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    return factory()

