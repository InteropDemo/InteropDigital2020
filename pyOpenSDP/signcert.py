#!/usr/bin/python3

from OpenSSL import crypto, SSL
import pprint
import sys
import os
import mysql.connector
import uuid
import random

#paths to private CA cert and key
ca_key_path ="/opt/opensdp/etc/keys/ca.key"
ca_crt_path="/opt/opensdp/etc/certs/ca.crt"

mydb = mysql.connector.connect(
        host="10.120.0.5",
        user="opensdp_rw",
        password="sXXXXXXXX",
        database="opensdp"
        )

updatecert_mysql = ("UPDATE clients "
                "SET "
                "sdpCert=%s, "
                "sdpkey=%s "
                "WHERE deviceId=%s")


def process_username(username):
    """
    using the username find the matching label field and returns a dictionary with
    deviced and a newly generated RSA key
    """
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("SELECT * from clients where binary label = '"+username+"'")
    user_dict = mycursor.fetchone()
    if user_dict:
        print("user found, returning info for:"+user_dict["deviceId"])
    else:
        sys.exit("user " + username + " not found. Did you add the user first?")
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA,2048)
    user_dict["sdpkey"]=crypto.dump_privatekey(crypto.FILETYPE_PEM,k).decode("utf-8")
    mycursor.close()  
    return user_dict


def generateCSR(nodename,key):
    """
    using deviceid and client key generates a CSR for that device
    with the CN set to the deviceId
    """

    csrfile = nodename +  '.csr'
    req = crypto.X509Req()
    # Return an X509Name object representing the subject of the certificate.
    req.get_subject().CN = nodename
    req.get_subject().countryName = 'US'
    req.get_subject().stateOrProvinceName = 'Somestate'
    req.get_subject().localityName = 'Somecity'
    req.get_subject().organizationName = 'SomeORG'
    req.set_pubkey(key)
    # Dump the certificate request req into a buffer string encoded with the type type.
    return req



def sign_cert(CSR,ca_private_key,ca_cert):
    """
    using CSR and CA private key and CA cert
    self sign the certificate
    """

    cert = crypto.X509()
    cert.set_serial_number(random.randrange(10000))
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365*24*60*60)
    cert.set_issuer(ca_cert.get_subject())
    cert.set_subject(CSR.get_subject())
    cert.set_pubkey(CSR.get_pubkey())
    cert.sign(ca_private_key, 'sha256')
    return cert


def main():
    """
    This program takes one parameter - username.
    It matches this with the "label" field in the database and retrieves the deviceId
    Then using the deviceId it populates the SDP key and crt fields for that user.
    NOTE: it CREATES and NEW key and cert EACH time it's run.
    """
    username = sys.argv[1]
    user_dict = process_username(username)
    ca_private_key_file = open(ca_key_path,'r')
    ca_private_key_text=ca_private_key_file.read()
    ca_cert_file = open(ca_crt_path)
    ca_crt_text=ca_cert_file.read()
    ca_private_key=crypto.load_privatekey(crypto.FILETYPE_PEM,ca_private_key_text)
    client_private_key=crypto.load_privatekey(crypto.FILETYPE_PEM,user_dict["sdpkey"])
    ca_crt=crypto.load_certificate(crypto.FILETYPE_PEM,ca_crt_text)
    newCSR = generateCSR(user_dict["deviceId"],client_private_key)
    newcert = sign_cert(newCSR,ca_private_key,ca_crt)
    user_dict["sdpCert"]=crypto.dump_certificate(crypto.FILETYPE_PEM, newcert).decode("utf-8")
    userdata=(user_dict["sdpCert"], user_dict["sdpkey"],user_dict["deviceId"])
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute(updatecert_mysql,userdata)
    mydb.commit()
    print(username + " sdp Certificate and Key updated")
    mycursor.close()
    mydb.close()



if __name__ == "__main__":
    main()
