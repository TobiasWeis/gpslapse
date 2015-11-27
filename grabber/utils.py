from datetime import datetime
import time

def tsms():
    '''time may only return 1 sec resolution '''
    # following block only returns milliseconds in current second
    #dt = datetime.now()
    #return dt.microsecond

    return int(round(time.time() * 1000))

def tsms2hr(tsms):
    '''convert timestamp in milliseconds to human readable datetime string'''
    dt = datetime.fromtimestamp(tsms/1000.0)
    return dt.strftime('%d %b %Y %H:%M:%S')
