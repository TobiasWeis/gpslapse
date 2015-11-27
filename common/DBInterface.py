#!/usr/bin/python
import datetime, time

import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import orm


class DBInterface(object):
    class Sensor(object):
        pass

    class Sequence(object):
        pass

    class Frame(object):
        pass

    class AnnotCar(object):
        pass

    class AnnotTaillight(object):
        pass

    def __init__(self):
        #self.engine = create_engine('sqlite://///home/weis/code/baltic_rallye_code/common/sequences.db')
        #self.engine = create_engine('sqlite://///home/pi/baltic_rallye_code/common/sequences.db')
        self.engine = create_engine('sqlite://///home/weis/Desktop/baltic_rallye_code/common/sequences.db')

        self.base = declarative_base()
        self.meta = MetaData(bind=self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        # first, get meta-data (structure and datatypes from all tables
        self.sequences = Table('sequences', self.meta, autoload=True, autoload_with=self.engine)
        self.sensors = Table('sensors', self.meta, autoload=True, autoload_with=self.engine)
        self.frames = Table('frames', self.meta, autoload=True, autoload_with=self.engine)
        self.annot_cars = Table('annot_cars', self.meta, autoload=True, autoload_with=self.engine)
        self.annot_taillights = Table('annot_taillights', self.meta, autoload=True, autoload_with=self.engine)

        # now, map the dummy-classes above to the tables, they inherit all fields
        # and can be used to insert or query from the database
        orm.mapper(self.Sensor, self.sensors)
        orm.mapper(self.Sequence, self.sequences)
        orm.mapper(self.Frame, self.frames)
        orm.mapper(self.AnnotCar, self.annot_cars)
        orm.mapper(self.AnnotTaillight, self.annot_taillights)

    def get_all_sequences(self):
        res = self.session.query(self.Sequence).all()
        return res

    def get_all_annotations(self):
        res = self.session.query(self.AnnotCar).all()
        return res


    def update_frame(self, frame):
        self.Frame = frame
        self.session.commit()

    def get_frame_uri_from_id(self, frame_id):
        s = self.session.query(self.Frame).filter(self.Frame.id==frame_id).first()
        return s.img_uri


    def get_frame_id_from_uri(self, frame_uri):
        s = self.session.query(self.Frame).filter(self.Frame.img_uri==frame_uri).first()
        return s.id

    def get_annot_cars(self, frame_id):
        annotcars = self.session.query(self.AnnotCar).filter(self.AnnotCar.id_frames==frame_id)
        return annotcars

    def insert_annot_taillight(self, tlu):
        self.session.add(tlu)
        self.session.commit()

    def get_annot_taillight(self, annot_id):
        print "Querying annot taillight with annot id: ", annot_id
        annot_tlus = self.session.query(self.AnnotTaillight).filter(self.AnnotTaillight.id_annot_cars==annot_id)
        return annot_tlus

    def insert_annot_car(self, frame_uri, ul, lr, bl, obj_id):
        # first, get frame id from uri
        id_frames = self.get_frame_id_from_uri(frame_uri)
        print "Got id %d for uri %s " % (id_frames, frame_uri)

        tmp = self.AnnotCar()
        tmp.id_frames = id_frames
        tmp.id_track = obj_id
        tmp.bbox_ul_x = ul[0] 
        tmp.bbox_ul_y = ul[1] 
        tmp.bbox_lr_x = lr[0] 
        tmp.bbox_lr_y = lr[1] 
        tmp.brakelight = bl

        try:
            self.session.add(tmp)
            self.session.commit()
            print "Commited to database !"
        except Exception, e:
            print "Error inserting: ", e
            self.session.rollback()

    def insert_sensor(self, name, flx=sqlalchemy.sql.null(),fly=sqlalchemy.sql.null(), ppx=sqlalchemy.sql.null(), ppy=sqlalchemy.sql.null(), k1=sqlalchemy.sql.null(), k2=sqlalchemy.sql.null(), k3=sqlalchemy.sql.null(), k4=sqlalchemy.sql.null(), k5=sqlalchemy.sql.null(), k6=sqlalchemy.sql.null(), tdc1=sqlalchemy.sql.null(),tdc2=sqlalchemy.sql.null()):
        tmp = self.Sensor()
        tmp.name = name
        tmp.flx = flx
        tmp.fly = fly
        tmp.ppx = ppx
        tmp.ppy = ppy
        tmp.k1 = k1
        tmp.k2 = k2
        tmp.k3 = k3
        tmp.k4 = k4
        tmp.k5 = k5
        tmp.k6 = k6
        tmp.tdc1 = tdc1
        tmp.tdc2 = tdc2

        try:
            self.session.add(tmp)
            self.session.commit()
        except Exception, e:
            print "Error inserting: ", e
            self.session.rollback()


        return tmp.id

    def get_sensor_id_from_name(self, sensor_name):
        s = self.session.query(self.Sensor).filter(self.Sensor.name==sensor_name).first()
        return s.id

    def insert_sequence(self, startdatetime, id_sensor, folder, simulated=False):
        tmp = self.Sequence()
        tmp.start_datetime = startdatetime
        tmp.id_sensor = id_sensor
        tmp.folder = folder
        tmp.simulated = simulated

        try:
            self.session.add(tmp)
            self.session.commit()
        except Exception, e:
            print "Error inserting sequence: ", e
            self.session.rollback()

        return tmp.id

    def insert_frame(self, id_sequence, img_uri, img_w, img_h, ts_cam, lat=sqlalchemy.sql.null(), lon=sqlalchemy.sql.null(), accx=sqlalchemy.sql.null(), accy=sqlalchemy.sql.null(), accz=sqlalchemy.sql.null(), avelx=sqlalchemy.sql.null(), avely=sqlalchemy.sql.null(), avelz=sqlalchemy.sql.null(), speed=sqlalchemy.sql.null(), exposure_time=sqlalchemy.sql.null(), altitude=sqlalchemy.sql.null(), ts_gps=sqlalchemy.sql.null(), ts_acc=sqlalchemy.sql.null(), ts_avel=sqlalchemy.sql.null(), context_nlanes=sqlalchemy.sql.null(), context_highwaytype=sqlalchemy.sql.null(), context_speedlimit=sqlalchemy.sql.null(), context_oneway=sqlalchemy.sql.null()):

        f = self.Frame()

        f.id_sequence = id_sequence
        f.img_uri = img_uri
        f.img_w = img_w
        f.img_h = img_h
        f.ts_cam = ts_cam
        f.lat = lat
        f.lon = lon
        f.accx = accx
        f.accy = accy
        f.accz = accz
        f.avelx = avelx
        f.avely = avely
        f.avelz = avelz
        f.speed = speed
        f.exposure_time = exposure_time
        f.altitude = altitude
        f.ts_gps = ts_gps
        f.ts_acc = ts_acc
        f.ts_avel = ts_avel
        f.context_nlanes = context_nlanes 
        f.context_highwaytype = context_highwaytype
        f.context_speedlimit = context_speedlimit
        f.context_oneway = context_oneway

        try:
            self.session.add(f)
            self.session.commit()
        except Exception, e:
            print "Error inserting sequence: ", e
            self.session.rollback()

        return f.id

    def get_sequence_meta(self, id_sequence):
        seq = self.session.query(self.Sequence).filter(self.Sequence.id == id_sequence).first()
        print "Got sequence for id ",id_sequence,": ", seq
        return seq

    def get_frames(self, id_sequence):
        frames = self.session.query(self.Frame).filter(self.Frame.id_sequence==id_sequence).all()
        print "Got %d frames from database." % len(frames)
        return frames


'''
this shows how to use the database-interface,
implements the test-functions,
'''
if __name__ == "__main__":
    db = DBInterface()
    # FIXME: differentiate between camera / gps / imu sensors ?
    # --- usual workflow for capture: 
    # 1 - try to insert sensor name
    # 2 - insert new sequence object
    # 3 - insert frames for sequence
    sensor_id = db.insert_sensor("Logitech C920")
    if sensor_id is None:
        print "Sensor was already in database, re-using"
        sensor_id = db.get_sensor_id_from_name("Logitech C920")
    print "Sensor id is:  ",  sensor_id
    sequence_id = db.insert_sequence(datetime.datetime.now(), sensor_id)
    print "Sequence-Id is: ", sequence_id
    for i in range(0,10):
        db.insert_frame(sequence_id, "/tmp/test%08d.png" % i, time.time())

