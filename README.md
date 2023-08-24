# HR-pQCT-Image-Processing-Server



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

## SCP set up
Public key authentication needs to be set up in both directions from the server to the HR-pQCT system to the computer that this software is running on

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
2. 


## Daemonizing the code:
A good guide for turning this software into a user service (a system service is not necessary) can be found here: https://github.com/torfsen/python-systemd-tutorial 

An example .service file is provided within the repo called image_processing.service 


