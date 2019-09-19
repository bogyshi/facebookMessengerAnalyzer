from user import User
import sys
import pdb
import numpy as np
import re
debug = True
class Chat:
    def _initUserClasses(self,isGM=False):
        """
        this is a private class to create user classes from raw JSON message data
        """
        counter = 0
        linkCounter=0
        imageCounter = 0
        emptyCounter = 0
        if(isGM):
            toIter = self.rawJSON
            textKey = "text"
            userKey = "user_id"
        else:
            toIter = self.rawJSON["messages"]
            textKey = "content"
            userKey= "sender_name"
        for u in self.userNames:
            self.users[u] = User(u)
        for x in toIter:
            counter = counter +1
            if(counter < 10):
                if(debug is True):
                    print(x[textKey])
                    print(x[userKey])
                    #print(x["reaction"])
            try:
                
                if('share' in x.keys()):
                    linkCounter+=1
                    print('found a link')
                elif('photos' in x.keys()):
                    imageCounter+=1
                    print('found a photo')
                elif('gifs' in x.keys()):
                    print('found a gif')
                elif('sticker' in x.keys()):
                    print('found a sticker')
                elif('video' in x.keys()):
                    print('found a vid')
                elif(textKey in x.keys()):
                    if(x[textKey] is None):
                        emptyCounter+=1
                    else:
                        if(isGM):
                            pass
                            #pdb.set_trace()
                        self.users[x[userKey]].messages.append(x[textKey])
                        toclean = x[textKey]
                        temp=re.sub(r'[\'*‘*’*]','',toclean.strip().lower())
                        temp=re.sub(r'[\,/.?!]',' ',temp)
                        self.users[x[userKey]].cleanMessages.append(temp)
                else:
                    print("this is getting real fishy")

            except KeyError:
                pass
        print("num messages: " + str(counter))
        print("num links sent: " + str(linkCounter))
        print("num images sent: " + str(imageCounter))
        print("numEmptyMessages: " + str(emptyCounter))
        for u in self.userNames:
            self.users[u].cleanMessages = np.array(self.users[u].cleanMessages)
                #print(x)
                #this should catch any non message
            #if counter is 20: #for debugging
            #    break
        for u in self.userNames:
            self.users[u].createDicts()
            self.users[u].removeStopWords() #OPTIONAL
        self.netDictionary = {}
        self.netMessages = 0
        self.netWords = 0

    def popSelfDict(self):
        for u in self.userNames:
            if (sys.version_info[0] < 3):
                toiter = self.users[u].dict.iteritems()
            else:
                toiter = self.users[u].dict.items()
            for key,val in toiter:
                if(key in self.netDictionary):
                    self.netDictionary[key]+=val
                else:
                    self.netDictionary[key]=val
            self.netWords += self.users[u].numWords
            self.netMessages += self.users[u].numMessages

    def updateUserStats(self):
        for u in self.userNames:
            self.users[u].updateStats()
            if(self.netDictionary):
                self.users[u].setDistinctWords(self.netDictionary,self.netWords,self.netMessages)

    def updateNames(self,convNames):
        for u in self.userNames:
            self.users[u].name = convNames[u]

    def printStats(self):
        for u in self.userNames:
            self.users[u].printTopX(10)

    def dumpChatStats(self):
        for u in self.userNames:
            self.users[u].dumpStats()

    def __init__(self,names,data,isGM=False):
        print("in init")
        self.rawJSON = data
        self.userNames = names
        self.users = {}
        self._initUserClasses(isGM)
        self.updateUserStats()
