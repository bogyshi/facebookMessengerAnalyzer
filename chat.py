from user import User
import sys
import pdb
import numpy as np
import re
import matplotlib.pyplot as plt
from spellchecker import SpellChecker
debug = False
class Chat:
    def _initUserClasses(self,isGM=False):
        """
        this is a private class to create user classes from raw JSON message data
        """
        counter = 0
        linkCounter=0
        imageCounter = 0
        emptyCounter = 0
        self.maxTokenLength=20 # might want to shorten this still
        self.maxMessageLength=20 # no need for messages this long
        self.orderedMessages=[]
        userMessageCount={}
        self.personOrder=[] # this will let us tag each message with the person who sent it
        if(isGM):
            toIter = [self.rawJSON]
            textKey = "text"
            userKey = "user_id"
        else:
            toIter = self.rawJSON
            textKey = "content"
            userKey= "sender_name"
        for u in self.userNames:
            self.users[u] = User(u)
            userMessageCount[u]=0
        for y in toIter:
            msToAppendInOrder=[]
            userTags=[]
            if(type(y) is dict):
                toiter2 = y['messages']
            else:
                toiter2 = y
            for x in toiter2:
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
                                #https://pypi.org/project/pyspellchecker/ #TODO USE AUTCORRECT TO FIX COMMON MISPELLINGS
                            #
                            toadd = x[textKey].lower().strip().rstrip()
                            self.users[x[userKey]].messages.append(toadd)
                            temp=re.sub(r'[\'*‘*’*]','',toadd.strip())# not exactly sure what this does tbh
                            temp=re.sub(r"([?.!¿:;\\/])",r" \1 ",temp) # puts space around punctuation (gets its own word)
                            #temp=re.sub(r'[\,/.?!:;]'," ",temp) # REPLACES punctuation with space instead (old version)

                            temp = re.sub('[^a-z0-9?\.\\!:;/ ]+','',temp).strip().rstrip() # removes all non alpha numeric characters but leaves spaces
                            self.users[x[userKey]].cleanMessages.append(temp)
                            userTags.append(x[userKey])
                            msToAppendInOrder.append(temp)
                            userMessageCount[x[userKey]]+=1
                    else:
                        print("this is getting real fishy")

                except KeyError:
                    pass
            self.orderedMessages.append(msToAppendInOrder[::-1])
            self.personOrder.append(userTags[::-1])

        self.orderedMessages = np.concatenate(np.array(self.orderedMessages),axis=None)
        self.personOrder = np.concatenate(np.array(self.personOrder),axis=None)

        #pdb.set_trace()
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
        custXAxis=np.arange(0,len(self.userNames),1)
        plt.bar(x=custXAxis,height=userMessageCount.values())
        plt.title("number of messages per user")
        hiddenNames = []
        for x in self.userNames:
            hiddenNames.append(x.split()[0])
        plt.xticks(custXAxis,hiddenNames)
        plt.xlabel("users")
        plt.ylabel("total number of messages")
        plt.savefig('./userMessageDistrib')

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

    def createCorpusAndTokens(self):
        messages=[]
        vocab = {}
        lenDistrib = {}
        messageDistrib = {}
        #pdb.set_trace()
        for m in self.orderedMessages:
            newMessage=""
            ms = m.split()
            mlen =len(m.split())
            if(mlen==0):
                pass
            elif(mlen>self.maxMessageLength):
                ms = ms[0:self.maxMessageLength]
            mlen=len(ms)
            for v in ms:
                #pdb.set_trace()
                holdit = v
                if(len(holdit)>=self.maxTokenLength):
                    holdit = v[0:self.maxTokenLength] # truncate words, honestly might just get rid of them

                if(holdit in vocab.keys()):
                    vocab[holdit]+=1
                else:
                    vocab[holdit]=1
                if(len(holdit) not in lenDistrib.keys()):
                    lenDistrib[len(holdit)]=1
                else:
                    lenDistrib[len(holdit)]+=1
                newMessage+=holdit+' '
            if(mlen not in messageDistrib.keys()):
                messageDistrib[mlen] = 1
            else:
                messageDistrib[mlen] += 1
            messages.append(newMessage)
        #print("Number unique mispelled words: "+str(len(setMisspelledWords)))
        wordFrequency={}
        breaks=[1000,500,200,100,50,10,5,3,1]
        heights = np.zeros(len(breaks))
        for x in vocab.keys():
            val = vocab[x]
            breakCounter = 0
            while(val<breaks[breakCounter]):
                breakCounter+=1
            heights[breakCounter]+=1
        custXAxis = np.arange(0,len(breaks),1)
        plt.bar(x=custXAxis,height=heights)
        plt.title("frequency of binned word frequencies")
        plt.xticks(custXAxis, np.array(breaks).astype(str))
        plt.xlabel("binned frequencies")
        plt.ylabel("frequency")
        plt.savefig('./wordFreqDistrib')
        plt.clf()
        plt.bar(x=lenDistrib.keys(),height=lenDistrib.values())
        plt.title("frequency of word lengths")
        plt.savefig('./wordLengthDistrib')
        plt.clf()
        plt.bar(x=messageDistrib.keys(),height=messageDistrib.values())
        plt.title("frequency of message lengths")
        plt.savefig('./messageLengthDistrib')
        return np.array(messages).flatten(),vocab,self.personOrder


    def getVocab(self):
        vocab = {}
        lenDistrib = {}
        for u in self.users.keys():
            for m in self.users[u].cleanMessages:
                t = m.split()
                for v in t:
                    if(v in vocab.keys()):
                        vocab[v]+=1
                    else:
                        vocab[v]=1
                    if(len(v) not in lenDistrib.keys() and len(v)<20):
                        lenDistrib[len(v)]=1
                    elif(len(v)<20):
                        lenDistrib[len(v)]+=1
        print(lenDistrib)
        plt.bar(x=lenDistrib.keys(),height=lenDistrib.values())
        plt.savefig('./cmononwson')
        return vocab

    def getMessages(self):
        messages=[]
        for u in self.userNames:
            messages.append(self.users[u].messages)
        return np.array(messages).flatten()

    def __init__(self,names,data,isGM=False):
        print("in init")
        self.rawJSON = data
        self.userNames = names
        self.users = {}
        self._initUserClasses(isGM)
        self.updateUserStats()
