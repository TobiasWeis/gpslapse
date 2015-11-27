--
-- File generated with SQLiteStudio v3.0.6 on Fr. Nov. 27 22:26:03 2015
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: sensors
DROP TABLE sensors;
CREATE TABLE sensors (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, flx REAL, fly REAL, ppx REAL, ppy REAL, k1 REAL, k2 REAL, k3 REAL, k4 REAL, k5 REAL, k6 REAL, tdc1 REAL, tdc2 REAL, name VARCHAR (50) UNIQUE);

-- Table: sequences
DROP TABLE sequences;
CREATE TABLE sequences (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, start_datetime DATETIME, simulated BOOLEAN, id_sensor INTEGER REFERENCES sensors (id) ON DELETE CASCADE NOT NULL, folder VARCHAR (200));

-- Table: frames
DROP TABLE frames;
CREATE TABLE frames (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, id_sequence INTEGER REFERENCES sequences (id) ON DELETE CASCADE, lat REAL, lon REAL, accx REAL, accy REAL, accz REAL, avelx REAL, avely REAL, avelz REAL, speed REAL, exposure_time REAL, altitude REAL, ts_gps INTEGER, ts_acc INTEGER, ts_avel INTEGER, context_nlanes INTEGER, context_highwaytype VARCHAR, context_speedlimit INTEGER, context_oneway BOOLEAN, img_uri VARCHAR (200), ts_cam INTEGER, img_w INTEGER, img_h INTEGER, context_streetname VARCHAR (200), ts_context INTEGER);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
