import user
import nltk
from collections import Counter
import csv
import re
#nltk.download('stopwords')
from nltk.corpus import stopwords

stpwrds = set(stopwords.words('english'))

class User:
    def __init__(self,name):
        print(name)
        self.name = name
        self.messages = []
        self.dict= {}
        self.dictMessages = {}
        self.stopWordCounts = {}
        self.dumbWords={
            'like':0,
            'i\'m':0,
            'im':0
        }
        for s in stpwrds:
            self.stopWordCounts[s]=0
        self.statCounter = None
        self.distinctCounter=None
        self.messageCounter=None
        self.distinctWords= []
        self.numWords= 0
        self.numMessages=0
        self.longestMessage=""
        self.longestMessagelen=0

    def createDicts(self):
        counter = 0
        for m in self.messages:
            self.numMessages+=1
            counter +=1

            temp=re.sub(r'[!?\']','',m.strip().lower())
            #temp=re.sub(r'[.]',' ',temp)
            if(len(temp.split(' '))>=2):
                if(len(temp.split(' '))>self.longestMessagelen):
                    self.longestMessage=temp
                    self.longestMessagelen=len(temp.split(' '))
                if(temp not in self.dictMessages):
                    self.dictMessages[temp]=1
                else:
                    self.dictMessages[temp]+=1
            for word in (m.strip().split(' ')):
                if(word == ""):
                    pass
                else:
                    self.numWords+=1
                    word = word.lower()
                    if(word not in self.dict and word not in stpwrds and word not in self.dumbWords):
                        self.dict[word] = 1
                    elif(word not in stpwrds and word not in self.dumbWords):
                        self.dict[word] += 1
                    elif word in stpwrds:
                        self.stopWordCounts[word]+=1
                    else:
                        self.dumbWords[word]+=1
        self.messageCounter = Counter(self.dictMessages)

    def setDistinctWords(self,totDict,netWords,netMessages):
        self.distinctCounter = Counter()
        for k , v in self.dict.iteritems():
            self.distinctCounter[k] = ( float(v*v)/(totDict[k]) ) * (float(self.numMessages)/netMessages)

    def dumpStats(self):
        with open('/home/avanroi1/messengerData/dumpFiles/'+self.name.replace(" ","_")+".csv","w") as csvdest:
            writer = csv.writer(csvdest)
            for key,val in self.statCounter.most_common():
                writer.writerow([key.encode('utf-8'),val])

    def removeStopWords(self):
        pass

    def updateStats(self):
        self.statCounter = Counter(self.dict)
    def printTopX(self,num):
        print(self.numMessages)
        print(self.name+" longest message: ")
        print(self.longestMessage)
        print(self.name+" top "+ str(num) +" most common messages: ")
        for message,count in self.messageCounter.most_common(num):
            print ('%s: %i' % (message,count))
        print(self.name+" top "+ str(num) +" most common words: ")
        for word,count in self.statCounter.most_common(num):
            print ('%s: %i' % (word,count))
        print(self.name+" top " + str(num) + " most distinct words: ")
        for word,count in self.distinctCounter.most_common(num):
            print ('%s: %f' % (word,count))
