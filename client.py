#!/usr/bin/sage -python
from sage.all import *
import socket
import pickle
import genreedsolomon as grs
import argparse

def main():
    #TODO decode to message or decode to code arg
    parser = argparse.ArgumentParser(description="GRS client")
    parser.add_argument("-P", "--port", default=666,type=int, dest="PORT", help="Socket port (default: 666)")
    args = parser.parse_args()

    HOST = "localhost"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((HOST, args.PORT))
        recv = s.recv(999999)   ##TODO recv based on pickle msg length
        data = pickle.loads(recv)
        server_args = data[0]
        C,D = grs.generalizedReedSolomon(server_args.o, server_args.n, server_args.k)
        print data[0],'\n',data[1]
        for i in range(len(data[1])):
            try:
                di = D.decode_to_message(data[1][i])
                print "#", i, data[1][i], "decoded to", di
            except (sage.coding.decoder.DecodingError, ValueError) as e:
                print "#", i, data[1][i], "decode failed"
                pass
    except socket.error as se:
        print se
        print "Check that your server is running or change port (-P PORT)"
    #TODO exceptions
    except Exception as e:
        print e
        raise
    finally:
        s.close()

if __name__ == "__main__":
    main()