# WHY?

This project is a quick and dirty example on how to extend the OpenSPA and OpenS
DP projects to be scalable witha centralize backend for the SDP and SPA discusio
ns in the 2020 InteropNet virtual booth https://interop.app.swapcard.com/event/i
nterop-digital-1/exhibitor/RXhoaWJpdG9yXzE4MTk2Ng%3D%3D

# PyOpenSDP

This is a replacement to the go Daemon for the OpenSDP project. It leverages mysql 
as a backend rather than files.  This repo also has a number support scripts 
to support the mysql backend.  This project also requires a working opensdp client
[GitHub - greenstatic/opensdp: A proof of concept Software Defined Perimeter (SDP) implementation using OpenSPA for service hiding](https://github.com/greenstatic/opensdp) 
as well as a working openspa install 
[GitHub - greenstatic/openspa: OpenSPA - An open and extensible Single Packet Authorization (SPA) implementation of the OpenSPA Protocol.(https://github.com/greenstatic/openspa).  I would recommend reading the doc for both of those projects to understand where this project fits.  

I would also double check this document: [opensdp/OpenSDP Setup Tutorial.md at master · greenstatic/opensdp · GitHub](https://github.com/greenstatic/opensdp/blob/master/docs/OpenSDP%20Setup%20Tutorial.md) .  

Keep in mind when reading these documents that all of the cert and key generation 
for the clients is down by the support scripts in this project, **however** this 
project still **requires the ca and server certs to be generated manually** using 
the openspa and opensdp documentation.   

Use of this project requires the installation of 
[GitHub - greenstatic/echo-ip: A small go web service to return the client&#39;s public IP.](https://github.com/greenstatic/echo-ip)  
on a publically accessable server somewhere.

# Content of this project

- pyOpenSDP.py
  
  - this is a replacement Daemon for the OpenSDP daemon that utilizes a mysql database for client information

- createuser.py
  
  - This script creates a user in the client table in the database and populates
 the record with a unique deviceId , openspa public key and the ospafile content

- signcert.py
  
  - This script find a user and then creates and self signed cert and key for the 
  MTLS conneciton used in the OpenSDP exchange.  It then populates those fields 
  in the corresponding database record.

- createconfig.py
  
  - This script creates a string that has the contents of a config.yaml file for
 a user.  This file us used by the OpenSDP client

- createtar.py
  
  - This script creates a tar file named 'username'.tar that contains all of the
 binaries and config files needed to run an OpenSDP client for that user on a linux 
 machine

- createwrapper.py
  
  - This is a wrapper script used when the OpenSDP client is calling the OpenSPA
 client to open ports.  It forces the use of a particular Echo-IP server since the 
 one hardcoded into OpenSPA doesn't appear to be active any longer

- sample.sql
  
  - Dump of an example mysql database showing configuration for pyOpenSPA. 
  
  - Has 3 demo users represented in the database
  
  - **NOTE**.  You will have to add services manually to services table in the database 
  and then associate the services and the user in the serviceMembership table

- user_directory_service.py
  
  - This script is a replacement script for the same named script in the 
  openspa-extension-scripts 
  [GitHub - greenstatic/openspa-extension-scripts: Extension scripts to use with the OpenSPA server.](https://github.com/greenstatic/openspa-extension-scripts) 
  Package.  This script modifies the behavoir of the openspa server to use the shared database for 
  client information rather than files on the server.


