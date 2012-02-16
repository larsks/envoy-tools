from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class TableNameMixin (object):

	@declared_attr
	def __tablename__(cls):
		return cls.__name__.lower()


class Report (TableNameMixin,Base):
	report_timestamp = Column(Integer, primary_key=True)
	pass

class Envoy (TableNameMixin,Base):
	serial_num = Column(String, primary_key=True)
	ip_addr = Column(String)
	mac_addr = Column(String)
	part_num = Column(String)
	timezone = Column(String)
	pass

class Device (TableNameMixin,Base):
	eqid = Column(String, primary_key=True)
	image_bits = Column(Integer)
	control_bits = Column(Integer)
	device_type = Column(Integer)
	admin_state = Column(Integer)
	condition_flags = Column(Integer)
	part_num = Column(String)
	pass

class Interval (TableNameMixin,Base):
	id = Column(Integer, primary_key=True)
	stat_duration = Column(Integer)
	interval_duration = Column(Integer)
	eqid = Column(String)
	pass

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

class Event (TableNameMixin,Base):
	id = Column(Integer, primary_key=True)
	pass

