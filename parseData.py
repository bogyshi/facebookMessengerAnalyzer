import os
import json
import argparse
import sys
#meant to prevent a stashed compiled file from preventing editing
sys.dont_write_bytecode = True
from chat import Chat



debug = False

def getJson(pathName):
    if(debug is True):
        print(os.getcwd())
        print(os.listdir('/home/avanroi1/messengerData/testData/MuAlphaNuGammaOmicron_34ea4e8c3b'))

    with open(pathName+'/message.json') as f:
        data = json.load(f)

    return data

def parseArgs():
    parser = argparse.ArgumentParser(description = "read in potential path name, potential user list, potential group name, and user name")
    parser.add_argument('username',type=str,help='username')
    args = parser.parse_args()
    return args

def getNumMessages(data):
    return len(data["messages"])

def main():
    weirdPathName = '/home/avanroi1/messengerData/testData/MuAlphaNuGammaOmicron_fd398840ae'
    data = getJson(weirdPathName)
    args = parseArgs()
    numMessages = getNumMessages(data)
    username = args.username
    nameVec = data["participants"]
    print(nameVec)
    nameVec = [x['name'].encode("ascii","ignore") for x in nameVec]
    #nameVec.append(username)
    if(debug is True):
        print(nameVec)
    c = Chat(nameVec,data)
    c.popSelfDict()
    c.updateUserStats()
    c.printStats()
    c.dumpChatStats()
main()
