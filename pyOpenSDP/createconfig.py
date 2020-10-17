#!/usr/bin/python3

# OpenSDP server (ip+port)
# server: XXX.XXX.XXX.XXX:33311
# ca-cert: "./ca.crt"
# certificate: "./fred.crt"
# key: "./fred.key"
# openspa-path: "./wrapper.sh"
# openspa-ospa: "clients/185a960b-5033-484f-a846-1f87f3a10cbf/client.ospa"
import sys

#ip address of pyOpenSDP server
SDPSERVER="XXX.XXX.XXX.XXX"
#port pyOpenSDP server is running on 
SDPPORT="33311"

def createconfig(username):
    """
    returns a string object containing the contents of a 
    openspa config.yaml file using parameters list at top of file
    """
    config =[]
    config.append("# OpenSDP server (ip+port)")
    config.append("server: " + SDPSERVER + ":" +SDPPORT)
    config.append('ca-cert: "./ca.crt"')
    config.append('certificate: "./' + username + '.crt"')
    config.append('key: "./' + username + '.key"')
    config.append('openspa-path: "./wrapper.sh"')
    config.append('openspa-ospa: "./'+ username + '.ospa"')
    configstring='\n'.join(config)
    return configstring


def main():
    username = sys.argv[1]
    print(createconfig(username))


if __name__ == "__main__":
    main()
