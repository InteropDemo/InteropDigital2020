#!/usr/bin/python3

import mysql.connector
import logging
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import ssl
import time
import pprint
import OpenSSL.crypto as crypto
import os

hostName = "0.0.0.0"
hostPort = 33311
CACERTPATH="/opt/opensdp/etc/certs/ca.crt"
SERVERCERTPATH="/opt/opensdp/etc/certs/server.crt"
SERVERKEYPATH="/opt/opensdp/etc/keys/server.key"

mydb = mysql.connector.connect(
        host="10.120.0.5",
        user="openspa_ro",
        password="wXXXXXXXXX",
        database="opensdp"
        )

LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
logging.basicConfig(level=LOGLEVEL)

def process_tags(tags):
    """splits tag field from database

    returns list of individual tags
    """

    #tags could/should probably be broken out into a seperate table
    tagslist=[x.strip() for x in tags.split(",")]
    return tagslist

def process_ports(ports):
    """splits ports field from database

    returns list of list  of port + protocol pairs
    """

    #ports could/should probably be broken out into a seperate table
    returnlist=[]
    portslist=[x.strip() for x in ports.split(",")]
    for port in portslist:
        port_proto_list=[x.strip() for x in port.split("/")]
        returnlist.append(port_proto_list)
    return returnlist

def get_service_json(client_device_id):
    """retrieves client service information based on deviceId

    returns json structure to be read by openspa client
    """
    return_dict={}
    return_dict["success"]=bool(True)
    return_dict["deviceId"]=client_device_id
    return_dict["services"]=[]
    logging.debug("attempting to retrieve service list for %s",client_device_id)
    mydb.ping(reconnect=True, attempts=3, delay=5)
    mycursor = mydb.cursor()
    mycursor.execute("SELECT service from serviceMembership where binary client = '"+client_device_id+"'")
    myresult = mycursor.fetchall()
    servicelist=[]
    for row in myresult:
        servicelist.append(row[0])
    logging.debug("service list=%s",pprint.pformat(servicelist))
    for client_service in servicelist:
        mycursor.execute("Select Name,IP,Ports,AccessType,Tags from services where binary Name = '"+client_service+"'")
        client_result = mycursor.fetchone()
        tempdict = {}
        tempdict["name"]=client_result[0]
        tempdict["ip"]=client_result[1]
        tempdict["ports"]=process_ports(client_result[2])
        tempdict["tags"]=process_tags(client_result[4])
        tempdict["accessType"]=[client_result[3]]
        return_dict["services"].append(tempdict)
    myresult=json.dumps(return_dict)
    mycursor.close()
    if myresult:
        return myresult
    else:
        return None


class MyServer(BaseHTTPRequestHandler):
    """long running web server process
    this is a python replacement to the go based OpenSPA server
    that uses a database backend rather than a file based backend

    responds only to /discover path. No returns
    """
    def do_GET(self):
        if self.path == "/discover":
            clientcert=self.connection.getpeercert(True)
            x509 = crypto.load_certificate(crypto.FILETYPE_ASN1,clientcert)
            commonName=x509.get_subject().CN
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(get_service_json(commonName).encode('utf-8'))
        else:
            # should the server just remain silent if not a discover?
            self.send_response(404)
            logging.error("invalid request from:%s",self.client_address[0])

myServer = HTTPServer((hostName, hostPort), MyServer)
myServer.socket = ssl.wrap_socket(myServer.socket, server_side=True, certfile=SERVERCERTPATH, keyfile="server.key",
            ca_certs=CACERTPATH,cert_reqs=ssl.CERT_REQUIRED,ssl_version=ssl.PROTOCOL_TLSv1_2)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    pass
mydb.close()
myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))


if __name__ == "__main__":
    # execute only if run as a script
    main()
