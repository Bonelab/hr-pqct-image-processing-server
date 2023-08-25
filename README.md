# HR-pQCT-Image-Processing-Server
Python 3.7 and above

This projects contains the server side and client side code for the HR-pQCT external image processing server. It is meant to be implemented as a service/daemon using systemctl in linux. Conda is required for setting up the environments to run the image processing algorithms, other than that the server itself uses python standard library packages. 

The Client side code is included, named EVAL_AUTOSEG_TRNSFR, it can be run with a submit script or by the UCT EVALUATION software itself.


## Server set up
1. Go to where you where you store your git repos
```
cd ~/Projects
```
2. Clone the HR-pQCT-Image-Processing-Server into your projects directory
```
git clone ---
```
3. Follow the instructions to set up the HR-pQCT segmentation model here https://github.com/Bonelab/HR-pQCT-Segmentation and test it to make sure that it can segment an image

4. In the the HR-pQCT-Image-Processing-Server directory open up constants.py
In constants.py there are 2 parameters
```
RAD_TIB_PATH_TO_ENV
RAD_TIB_PATH_TO_START
```
Set RAD_TIB_PATH_TO_ENV to be the full path to the location of your python interpreter for the bl_torch environment
Set RAD_TIB_PATH_TO_START to be the full path to the segment.py script for the HR-pQCT segmentation model

5. To run the code just call python main.py

   
## SCP/SFTP set up
Public key authentication needs to be set up in both directions from the server to the HR-pQCT system to the computer that this software is running on.

A guide for setting up public key authentication from linux to OpenVMS can be found on the BOYD drive.


Pub-Key Authentication from OpenVMS to Linux server

1. If you have not already generated a public key, generate one using this command
```
$ mcr DKA0:[SYS0.SYSCOMMON.SYSEXE]TCPIP$SSH_SSH-KEYGEN2.EXE "-P" -t rsa
```
or if that doesn't work
```
$ mcr SYS$SYSTEM:TCPIP$SSH_SSH-KEYGEN2.EXE "-P" -t rsa
```
the key can be found in this location 
```
DISK1:[XTREMECT2.SSH2]
```
and it should be named
```
ID_RSA_2048_A.PUB
```
2. Tranfer it to the computer you are setting this up on
3. You will need to open up the key in a text editor and it will look like this example
```
---- BEGIN SSH2 PUBLIC KEY ----
Subject: xtremect2
Comment: "2048-bit rsa, xtremect2@openvms.example.ca, Mon Jan 1 2000 1\
12:00:00"
AAAAB3NzaC1yc2EAAAADAQABAAABAQCrOWA9JxeXfrHJCWVS1DF0zJbklJO1ZeaTFRRFmq
vT9I7wXjUK7AvKexEyvq+7dkm4lRdNexzdi2Ck2FrEaC4j2UwiKxIa6QMNeJcvuiXXufEo
dFPrFFBwTS1LkFzZrmzFGTdyV21hI6H1+GsUUSVp+q/Oap6imfFy3CyRSdU2SE+vM+bqtI
CqMgT45RFlr7qPATFvmgGU2BiecS5ZB8v6S0iadIGSqakN8zDVoSDMzRY2fvr5HDlFFQMY
z6w6kjoa210P2yE3LzitNRFfNmZ1UBu2c98HwscRO9+nwkXAzfNbnd3wNOrBCQK8tsBW7l
kR1MF2NyOwIQv3F5FjGl1X
---- END SSH2 PUBLIC KEY ----
```
4. You will need to remove all line breaks that are in the key itself and format it to look like this
```
ssh-rsa
AAAAB3NzaC1yc2EAAAADAQABAAABAQCrOWA9JxeXfrHJCWVS1DF0zJbklJO1ZeaTFRRFmqvT9I7wXjUK7AvKexEyvq+7dkm4lRdNexzdi2Ck2FrEaC4j2UwiKxIa6QMNeJcvuiXXufEodFPrFFBwTS1LkFzZrmzFGTdyV21hI6H1+GsUUSVp+q/Oap6imfFy3CyRSdU2SE+vM+bqtICqMgT45RFlr7qPATFvmgGU2BiecS5ZB8v6S0iadIGSqakN8zDVoSDMzRY2fvr5HDlFFQMYz6w6kjoa210P2yE3LzitNRFfNmZ1UBu2c98HwscRO9+nwkXAzfNbnd3wNOrBCQK8tsBW7lkR1MF2NyOwIQv3F5FjGl1X xtremect2@openvms.example.ca
```
5. Once you have done that, you can add the reformatted key to your autorized_keys file
6. You will then need to add some lines to your ssh_config and sshd_config files
   ssh_config:
   ```
    KexAlgorithms diffie-hellman-group1-sha1
    HostKeyAlgorithms ssh-dss
    MACs hmac-sha1,umac-64@openssh.com

   ```
   sshd_config
   ```
   KexAlgorithms diffie-hellman-group1-sha1
   HostKeyAlgorithms ssh-dss
   ```
   

## Turning the code into a service:
A good guide for turning this software into a user service (a system service is not necessary) can be found here: https://github.com/torfsen/python-systemd-tutorial 

An example .service file is provided within the repo called image_processing.service 


