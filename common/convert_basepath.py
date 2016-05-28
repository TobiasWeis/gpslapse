#!/usr/bin/python
'''
open database, read basepath of sequences, change it to the current machine's basepath
'''

import sqlite3
import os.path

conn = sqlite3.connect('sequences.db')
c = conn.cursor()

new_basepath = '/home/shared/data/TobisGpsSequence/'
new_basepath = '/data/'
new_basepath = '/media/weis/Transcend/Testfahrt/'

rows = c.execute('SELECT * FROM sequences')

mylist = []

for row in rows:
    s_id = row[0]
    s_folder = row[4]

    old_basepath = os.path.dirname(row[4])
    old_folder = os.path.basename(os.path.normpath(row[4]))
    new_folder = new_basepath + old_folder 

    mylist.append([s_id, new_folder + "/"])

for e in mylist:
    c.execute('UPDATE sequences SET folder="%s" WHERE id=%d;' % (e[1], e[0]))
    print "Changing folder to", e[1]
conn.commit()
conn.close()
