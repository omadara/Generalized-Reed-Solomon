#!/usr/bin/sage -python
from sage.all import *
import sys
import thread
import socket
import pickle
import genreedsolomon as grs
import argparse

def main(argv):
    HOST = "localhost"

    args = parseArguments(argv)
    #TODO continue only of args generate grs
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((HOST, args.PORT))
        s.listen(5)
        print "Server started"
        while 1:
            conn, addr = s.accept()
            thread.start_new_thread(send2Client, (conn, addr, args))
    except KeyboardInterrupt:
        print "Terminating server"
    except socket.error as se:
        print se
        print "Check that your specified port", args.PORT, "is available"
    #TODO sage exceptions
    except Exception as e:
        print e
        raise
    finally:
        print "Socket closed"
        s.close()

def send2Client(client, address, args):
    print "New client @", address
    try:
        C,D = grs.generalizedReedSolomon(args.o, args.n, args.k)
        msg = [C.random_element() for i in range(args.msgnum)]
        err = grs.addRandomErrors(msg, args.error, C)
        for i in range(len(msg)):
            print "#",i,msg[i], err[i]
        client.send( pickle.dumps((args, err)))
    #TODO exceptions
    except Exception as e:
        print e
    finally:
        client.close()

def parseArguments(args):
    parser = argparse.ArgumentParser(description="Generalized Reed-Solomon",
            epilog="Examples: server.py -qo59 -n40 -k12 -p0.23")
    #####TODO: accept order like -o 2**4
    parser.add_argument("-o", "--order", required=True, type=int, dest="o", help="GRS finite field's order")
    parser.add_argument("-q", "--primary", action='store_true', dest="primGF", help="Set GRS finite field's order to next primary")
    parser.add_argument("-n", required=True, type=int, dest="n", help="GRS evaluation points")
    parser.add_argument("-k", required=True, type=int, dest="k", help="GRS dimension")
    parser.add_argument("-m", "--messages", default=20, type=int, dest="msgnum", help="Number of messages to send")
    error_group = parser.add_mutually_exclusive_group()
    error_group.add_argument("-e", default=0, type=int, dest="error", help="Number of errors added to each message (default: 0)")
    error_group.add_argument("-E", type=int, nargs=2, metavar=("E0", "E1"), dest="error", help="Random number (between E0 and E1) of errors added to each message")
    error_group.add_argument("-p", type=float, choices=[Range(0.0, 1.0)], metavar="ERROR", dest="error", help="Error probabillity")
    parser.add_argument("-P", "--port", default=666,type=int, dest="PORT", help="Socket port (default: 666)")
    #TODO: message input from file
    #TODO: --verbose
    return parser.parse_args(args)

#copied from https://stackoverflow.com/a/12117089
class Range(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end
    def __eq__(self, other):
        return self.start <= other < self.end
    def __repr__(self):
        return '{0}-{1}'.format(self.start, self.end)

if __name__ == "__main__":
    main(sys.argv[1:])