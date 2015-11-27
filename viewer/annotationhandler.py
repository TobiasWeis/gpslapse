'''
this file handles filenames and their annotations
Currently implemented: textfiles
'''
import sqlite3

class AnnotationHandler():
    def __init__(self, foldername):
        self.foldername = foldername
        print "AnnotationHandler for folder ", self.foldername
        try:
            self.con = sqlite3.connect('db')
        except:
            print "Database with name %s not found." % (annotdb)
        print "AnnotationHandler connected to database."
        self.checkFolder()

    '''
    check if folder already exists in database
    '''
    def checkFolder(self):
        cur = self.con.cursor()
        qr = "SELECT id FROM folders where foldername = \"%s\"" % (self.foldername)
        cur.execute(qr)
        rows = cur.fetchall()
        if len(rows) > 0:
            self.folderid = rows[0][0]
            print "Folder was already there, with id", self.folderid
        else:
            print "Inserting folder"
            qr = "INSERT INTO folders(foldername) VALUES (\"%s\")" % (self.foldername)
            cur.execute(qr)
            self.con.commit()
            self.folderid = cur.lastrowid

    '''
    for export - get all annotations
    '''
    def getAllAnnotations(self, style="caffe"):
        cur = self.con.cursor()
        # caffe needs: filename_without_folder label
        if style == "caffe":
            annotations = []
            qr = "SELECT filename, id_label  FROM annotations,files WHERE annotations.id_files = files.id AND files.id_folder = %d" % (self.folderid)
            cur.execute(qr)
            rows = cur.fetchall()
            if len(rows) > 0:
                for r in rows:
                    annotations.append("%s %d" % (r[0], int(r[1])-1)) # labels should start at 0
                return annotations
            else:
                print "No annotations found to export"
        else:
            print "I do not recognize this style: ", style


    def setLabel(self, filename, label):
        # get fileid
        fileid = self.getfileid(filename)

        # get labelid
        labelid = self.getlabelid(label)

        res = self.getLabel(filename)
        if not res:
            cur = self.con.cursor()
            # insert label
            qr = "INSERT INTO annotations(id_files, id_label) VALUES (%d, %d)" % (fileid, labelid)
            cur.execute(qr)
            self.con.commit()
            print "Inserted new row for annotation"
        else:
            cur = self.con.cursor()
            qr = "UPDATE annotations SET id_label=%d WHERE id_files=%d " % (labelid, fileid)
            cur.execute(qr)
            self.con.commit()
            print "Changed label"


    def addLabel(self, label):
        print "Adding label ", label
        cur = self.con.cursor()
        # insert label
        qr = "INSERT INTO labels(id_folder, label) VALUES (%d, \"%s\")" % (self.folderid, label)
        cur.execute(qr)
        self.con.commit()


    '''
    return all labels associated with that dataset
    '''
    def getAllLabels(self):
        cur = self.con.cursor()
        # insert label
        qr = "SELECT id,label FROM labels WHERE id_folder=%d" % (self.folderid)
        cur.execute(qr)
        rows = cur.fetchall()
        ret = [[-1,""]]
        for r in rows:
            print "Appending [%s, %s]" % (r[0], r[1])
            ret.append([r[0],r[1]])
        print "%d labels found" % (len(rows))
        return ret

    def getlabelid(self, label):
        cur = self.con.cursor()
        qr = "SELECT id FROM labels WHERE label=\"%s\"" % (label)
        cur.execute(qr)
        rows = cur.fetchall()

        if len(rows) == 0:
            print "That label does not exist yet"
            return
        if len(rows) == 1:
            print "Label has id ", rows[0][0]
            labelid = rows[0][0]
        if len(rows) > 1:
            print "Label is duplicated in database !"
            return
        return labelid

    def getImagesWithLabel(self, label, limit = -1):
        cur = self.con.cursor()
        if label == "":
            if limit == -1:
                qr = "SELECT filename FROM annotations,labels,files WHERE annotations.id_label = labels.id AND annotations.id_files = files.id" % (label)
            else:
                qr = "SELECT filename FROM annotations,labels,files WHERE annotations.id_label = labels.id AND annotations.id_files = files.id LIMIT %d" % (label, limit)
        else:
            if limit == -1:
                qr = "SELECT filename FROM annotations,labels,files WHERE labels.label = \"%s\" AND annotations.id_label = labels.id AND annotations.id_files = files.id" % (label)
            else:
                qr = "SELECT filename FROM annotations,labels,files WHERE labels.label = \"%s\" AND annotations.id_label = labels.id AND annotations.id_files = files.id LIMIT %d" % (label, limit)
        print qr
        cur.execute(qr)
        rows = cur.fetchall()
        fs = []
        for r in rows:
            fs.append(r)
        return fs


    def insertnewfile(self, filename):
        cur = self.con.cursor()
        qr = "INSERT INTO files(id_folder, filename) VALUES (%d, \"%s\")" % (self.folderid, filename)
        cur.execute(qr)
        self.con.commit()
        # get file id and return it
        print "INSERTED FILE WITH ID", cur.lastrowid
        return cur.lastrowid
    
    def getfileid(self, filename):
        cur = self.con.cursor()
        qr = "SELECT id FROM files WHERE filename=\"%s\"" % (filename)
        cur.execute(qr)
        rows = cur.fetchall()

        if len(rows) == 0:
            print "That file does not exist yet"
            return self.insertnewfile(filename)
        if len(rows) == 1:
            print "File has id ", rows[0][0]
            fileid = rows[0][0]
        if len(rows) > 1:
            print "File is duplicated in database !"
            return
        return fileid

    '''
    get the label of a specific file
    '''
    def getLabel(self, filename):
        cur = self.con.cursor()
        fileid = self.getfileid(filename)
        qr = "SELECT label FROM annotations,labels WHERE annotations.id_label == labels.id AND annotations.id_files == %d" % (fileid)
        #print qr
        cur.execute(qr)
        rows = cur.fetchall()
        print "#Rows for getLabel: ", len(rows)
        if len(rows) == 0:
            print "No labels"
            return False
        else:
            return rows[0]
            
