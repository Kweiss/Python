#!/usr/bin/env python

###########################################
#  WWC Meetup
#     Gnip and Arduino Fun!
#     2013-07-10
#
# Make sure you have pyserial and requests 
# packages install and working for your python 
# installation:
#    Pyserial http://pyserial.sourceforge.net/
#    Requests http://docs.python-requests.org/en/latest/
###########################################

###
# copy the result of your 'ls /dev/ .....' here:
usbmodem = 'tty.usbmodem1411'
# usbmodem = 'tty.usbmodemfd121'
###


import serial
import requests
import json
import sys
import time

###
# Temporary Gnip interface to real time social data
#
TOP_URL = "http://shendrickson3.gnip.com:8090/redr8r/v1/top.json"
# Example output
#  {
#          timestamp: 1373322884,
#          version: "v1",
#          topkeys: {
#              blue: 862,
#              justin: 1270,
#              egypt: 716,
#              sun: 1118,
#              one: 383,
#              black: 2428,
#              bieber: 1323,
#              amp: 407,
#              red: 1623,
#              obama: 690
#              }
#          }
CNT_URL = "http://shendrickson3.gnip.com:8090/redr8r/v1/%s/count.json"
# Example output
# {
#         keys: {
#             black: {
#                 count: 17628
#                 }
#             },
#         timestamp: 1373324445,
#         version: "v1"
#         }
###########################################

try:
    # *nix / Mac OS X
    serial_dev = '/dev/' + usbmodem
    #On Windows, try uncommenting the following:
    #serial_dev = 0
    ser = serial.Serial(serial_dev, 9600, timeout=0)
except serial.serialutil.SerialException, e:
    print >>sys.stderr, "Check your serial port definition: (%s)"%(str(e))
    ser = None
###########################################

##################################################
# Terms you want to track -- discussion in meetup
# (<= 9 terms)
#
terms_to_watch = ["love", "blue"]
#
##################################################


# simple protocol for communication with arduino
terms = { terms_to_watch[i]:1+i for i in range(len(terms_to_watch))}

# This function writes to the arduino through serial port
def write_term(x):
    res = ""
    if ser:
        ser.write(str(x)[0])
        # Synchronize with arduino
        # Read empty buffer until arduino writes back something besides 'c'
        while res == "" or res == 'c':
            res = ser.read(1)
    else:
        print >>sys.stderr, "No serial connection detected."
    return res   

TIME_DELAY = 2              # wait at least this long between fetches
THRESHOLD = 20./TIME_DELAY  # minimum rate (count of activities over TIME_DELAY) needed in order to signal arduino

if __name__=="__main__":
    # initial the counters for the last terms read from the server
    last = {x:0 for x in terms}
    # build a format string of the right length
    tmpfmt = "%s:"*len(terms)
    req_string = tmpfmt%tuple(terms.keys())
    # repeat this forever
    last_timestamp = time.time()
    while True:
        # how long since last fetch?
        delta_t = time.time() - last_timestamp
        if delta_t < TIME_DELAY:
            # calculate sleep time to make up the difference
            time.sleep(TIME_DELAY - delta_t)
        # new delta_t for rate calculation
        delta_t = time.time() - last_timestamp
        # update last timestamp
        last_timestamp = time.time()
        # fetch results from server
        response = requests.get(CNT_URL%req_string)
        try:
            res_dict = json.loads(response.text)
        except ValueError:
            print >>sys.stderr, "Invalid json:", response.text
        # let's see some output
        # print >>sys.stderr,response.text
        # step through the terms and do something
        print '*'
        for c in terms:
            if c in res_dict["keys"]:
                # calculate count diffs from last time through the loop
                diff = int(res_dict["keys"][c]["count"]) - last[c]
                rate = float(diff)/delta_t
                if rate > THRESHOLD:
                    # write to the arduino over the serial port
                    print "term: %10s  count change: %5d  rate: %3.2f/sec blinks: %d  reponse: %s"%(
                            c, diff, rate, terms[c], write_term(terms[c])
                            )
                    # keep track of counts for next diff
                    last[c] = int(res_dict["keys"][c]["count"])
                else:
                    print "term: %10s  skipping: %3.2f <= %3.2f"%(c, rate, THRESHOLD)