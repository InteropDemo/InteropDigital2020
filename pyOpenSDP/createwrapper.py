#!/usr/bin/python3

# #!/bin/bash
# ./openspa-client_linux "$@" \
# 	--echo-ipv4-server ECHOIP_SERVER_URL \
# 	-v

import sys

ECHOIP_SERVER_URL="http://server.example.tld:8080/"

def createwrapper():
    """
    returns string containing bash script that wraps the openspa-client
    https://github.com/greenstatic/openspa
    for use with pyOpenSDP
    """
    
    wrapper =[]
    wrapper.append("#!/bin/bash")
    wrapper.append('./openspa-client_linux "$@" \\')
    wrapper.append('--echo-ipv4-server ' + ECHOIP_SERVER_URL)
    wrapperstring='\n'.join(wrapper)
    return wrapperstring


def main():
    username = sys.argv[1]
    print(createwrapper(username))


if __name__ == "__main__":
    main()
