from user import User
debug = True
class Chat:
    def _initUserClasses(self):
        """
        this is a private class to create user classes from raw JSON message data
        """
        counter = 0
        for u in self.userNames:
            self.users[u] = User(u)
        for x in self.rawJSON["messages"]:
            counter = counter +1
            if(counter < 10):
                if(debug is True):
                    print(x["content"])
                    print(x["sender_name"])
                    #print(x["reaction"])
            try:
                self.users[x["sender_name"]].messages.append(x["content"])

            except KeyError:
                pass
        print("num messages: " + str(counter))
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
            for key,val in self.users[u].dict.iteritems():
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

    def printStats(self):
        for u in self.userNames:
            self.users[u].printTopX(10)

    def dumpChatStats(self):
        for u in self.userNames:
            self.users[u].dumpStats()

    def __init__(self,names,data):
        print("in init")
        self.rawJSON = data
        self.userNames = names
        self.users = {}
        self._initUserClasses()
        self.updateUserStats()
