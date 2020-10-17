#!/usr/bin/python3

import pexpect
import tempfile
import os
import sys
import mysql.connector

#path to OpenSPA tools binary
#https://github.com/greenstatic/openspa
OPENSPA_TOOLS="/opt/openspa/bin/openspa-tools"
#server public key generated with above tool
SERVER_PUBLIC_KEY="/opt/openspa/etc/keys/server.pub"
OPENSDP_SERVER_IP="XXX.XXX.XXX.XXX"
ECHOIP_SERVER_URL="http://myserver.example.tld"

mydb = mysql.connector.connect(
        host="10.120.0.5",
        user="opensdp_rw",
        password="sXXXXXXX",
        database="opensdp"
        )

adduser_mysql = ("INSERT INTO clients "
                "(deviceId,label,spapubkey,ospafile) "
                "VALUES (%s, %s, %s, %s)")

def adduser(username):
    """
    Using the openspa-tools binary and the openspa server public key 
    as well as the username
    creates a record in the clients table in the database  with a newly generated deviceID(UUID),
    label that matches the username, freshly generated rsa public key and the ospa config file
    """

    with tempfile.TemporaryDirectory() as tmpdirname:

        os.chdir(tmpdirname)
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute("SELECT * from clients where binary label = '"+username+"'")
    # myresult = mycursor.fetchone().encode('utf-8').decode('unicode_escape')
        user_dict = mycursor.fetchone()
        if user_dict:
            sys.exit("user found, exiting")
        command =  OPENSPA_TOOLS + " gen-client " + SERVER_PUBLIC_KEY + " -o " + tmpdirname
        p = pexpect.spawn(command,cwd=os.path.dirname(tmpdirname))
        p.expect('server\"\):')
        p.sendline("")
        p.expect("Dv4\):")
        p.sendline("")
        p.expect("\"\"\):")
        p.sendline(OPENSDP_SERVER_IP)
        p.expect("22211\):")
        p.sendline("")
        p.expect(".org\):")
        p.sendline(ECHOIP_SERVER_URL)
        p.expect("keypair\):")
        p.sendline("")
        p.expect(pexpect.EOF)
        words=p.before.split()
        ospafilepath=words[7].split(b'=')[1]
        userpubkeypath=words[8].split(b'=')[1]
        uuid=userpubkeypath.split(b"/")[3].replace(b".pub",b"")
        print(uuid)
        with open(ospafilepath) as f:
            ospastring=f.read()
        with open(userpubkeypath) as f:
            userpubkeystring=f.read()
        user_dict={}
        deviceId=uuid.decode('utf-8')
        label=username
        spapubkey=userpubkeystring
        ospafile=ospastring
        userdata=(deviceId,label,spapubkey,ospafile)
        mycursor.execute(adduser_mysql,userdata)
        print(label + " added")
        mydb.commit()
        mycursor.close()
        mydb.close()


def main():
    """
    program takes one parameter: username and creates a record in the clients table in the
    database for that user
    """
    username = sys.argv[1]
    adduser(username)


if __name__ == "__main__":
    main()

