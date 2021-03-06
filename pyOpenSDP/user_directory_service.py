#!/usr/bin/env python3

# Copyright 2018 Gregor R. Krmelj
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ----------------------------------------------------------------------------------------------------------------------

# OpenSPA user directory service extension script. This script will return to stdout
# the user's public key returned from a central database
#
# Usage:
#   python3 user_directory_service.py GET_USER_PUBLIC_KEY <client_device_id>
#
# The users UUID should be in the UUIDv4 format WITH DASHES.
#
# In case we come across an error (bad script parameters) we will log the
# error and return a non zero exist status.
#
#
# Supported OpenSPA server user directory service extension script commands:
#   * GET_USER_PUBLIC_KEY
#
# VERSION: 1.0.1-CGS

import sys
import logging
from uuid import UUID
from os.path import join
import os
import mysql.connector


mydb = mysql.connector.connect(
        host="10.120.0.5",
        user="openspa_ro",
        password="wXXXXXXXXXXXXX",
        database="opensdp"
        )



EXIT_UNKNOWN_COMMAND = 1
EXIT_BAD_INPUT = 2
EXIT_NO_PUBLIC_KEY_FOUND = 3

GET_USER_PUBLIC_KEY = "GET_USER_PUBLIC_KEY"

supported_commands = [GET_USER_PUBLIC_KEY]
logging.basicConfig(filename='user_directory_service.log')
logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)


def main():
    if len(sys.argv) < 2:
        logger.error("Did not run any command, here are all the supported commands: %s", supported_commands)
        sys.exit(EXIT_UNKNOWN_COMMAND)

    command = sys.argv[1].upper()

    if command == GET_USER_PUBLIC_KEY:

        if len(sys.argv) != 3:
            logger.error("%s expects the following argument format: %s <client_device_id>", GET_USER_PUBLIC_KEY,
                         GET_USER_PUBLIC_KEY)
            sys.exit(EXIT_BAD_INPUT)

        client_device_id = valid_uuid(sys.argv[2])
        if not client_device_id:
            logger.error("%s expects a valid client device UUID", GET_USER_PUBLIC_KEY)
            sys.exit(EXIT_BAD_INPUT)

        pub_key = command_get_user_public_key(client_device_id)

        if pub_key:
            sys.stdout.write(pub_key)
            sys.stdout.flush()
            sys.exit(0)
        else:
            # File does not exist
            logger.info("User with the UUID: %s, does not have a public key in the public key directory", client_device_id)
            sys.exit(EXIT_NO_PUBLIC_KEY_FOUND)

    else:
        logger.error("%s is not a supported command, here is a list of supported commands: %s", command,
                     supported_commands)
        sys.exit(EXIT_UNKNOWN_COMMAND)


def command_get_user_public_key(client_device_id):
    """
    Returns the clients's device public key or None if the client's device public key is not found.
    """
    logger.info("attempting to retrieve public key for %s",client_device_id)
    mycursor = mydb.cursor()
    mycursor.execute("SELECT spapubkey from clients where binary deviceId = '"+client_device_id+"'")
   # myresult = mycursor.fetchone().encode('utf-8').decode('unicode_escape')
    myresult = mycursor.fetchone()
    logger.debug("result from key retrieval=%s",myresult)
    if myresult:
        return myresult[0]
    else:
        return None

def valid_uuid(s):
    """
    Checks if parameter is a valid UUID, if it is it returns it (as a string) otherwise
    return None.
    """
    try:
        UUID(s)
        return s
    except:
        return None


if __name__ == "__main__":
    main()
