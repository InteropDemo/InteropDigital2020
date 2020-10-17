#!/usr/bin/python3

import mysql.connector
import tarfile
import pprint
import sys
import io
import createconfig as config
import createwrapper as wrapper

#https://github.com/greenstatic/openspa
#path to private OpenSPA CA cert
CACERTFILE="/opt/opensdp/etc/certs/ca.crt"
#path to opensdp-client binary
OPENSDPCLIENT="/opt/opensdp/bin/opensdp-client"
#path to the openspa-client
OPENSPACLIENT="/opt/openspa/bin/openspa-client_linux"


mydb = mysql.connector.connect(
        host="10.120.0.5",
        user="opensdp_rw",
        password="sXXXXXX",
        database="opensdp"
        )


def createtar(username):
    """
    takes one parameter - username 
    Username should map to a and entry in the "label" field in the database
    using this information this routines creates and writes a tar file name
    'username'.tar containing:
    - private ca cert
    - client cert named 'username'.crt
    - client key named 'username'.key
    - openspa config file anmed 'username'.ospa
    - opensdp-client linux binary
    - openspa-client_linux linux binary
    - openspa config file named config.yaml
    - openspa bash script named wrapper.sh used by opensdp-client

    """
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("SELECT * from clients where binary label = '"+username+"'")
    user_dict = mycursor.fetchone()
    mycursor.close()
    mydb.close()
    if user_dict:
        print("user found, creating tar file for "+user_dict["label"])
    else:
        sys.exit("user " + username + " not found. Did you add the user first?")
    tarfilename=username + ".tar"
    with tarfile.open(tarfilename,"w") as tar:
        cacert_file = open(CACERTFILE,'r')
        caitem=cacert_file.read().encode()
        ospaitem=user_dict["ospafile"].encode()
        certitem=user_dict["sdpCert"].encode()
        keyitem=user_dict["sdpkey"].encode()
        info=tarfile.TarInfo(name="ca.crt")
        info.size=len(caitem)
        tar.addfile(tarinfo=info, fileobj=io.BytesIO(caitem))
        info=tarfile.TarInfo(name=username+".ospa")
        info.size=len(ospaitem)
        tar.addfile(tarinfo=info, fileobj=io.BytesIO(ospaitem))
        info=tarfile.TarInfo(name=username+".crt")
        info.size=len(certitem)
        tar.addfile(tarinfo=info, fileobj=io.BytesIO(certitem))
        info=tarfile.TarInfo(name=username+".key")
        info.size=len(keyitem)
        tar.addfile(tarinfo=info, fileobj=io.BytesIO(keyitem))
        configitem=config.createconfig(username).encode()
        info=tarfile.TarInfo(name="config.yaml")
        info.size=len(configitem)
        tar.addfile(tarinfo=info, fileobj=io.BytesIO(configitem))
        wrapperitem=wrapper.createwrapper().encode()
        info=tarfile.TarInfo(name="wrapper.sh")
        info.size=len(wrapperitem)
        info.mode=0755
        tar.addfile(tarinfo=info, fileobj=io.BytesIO(wrapperitem))
        tar.add(OPENSDPCLIENT,arcname="opensdp-client")
        tar.add(OPENSPACLIENT,arcname="openspa-client_linux")



def main():
    username = sys.argv[1]
    createtar(username)


if __name__ == "__main__":
    main()
