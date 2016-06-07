class Settings():
    def __init__(self):
        self.outdir = "./tmp_files/"
        try:
            os.mkdir(self.outdir)
        except:
            print "Directory already exists"

