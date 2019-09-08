import os
import json
import argparse
import sys
import pdb
import numpy as np
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline

#meant to prevent a stashed compiled file from preventing editing
sys.dont_write_bytecode = True
from chat import Chat



debug = False
doModel = False

def doPipeLineAcc(bm,td,targs):
    ns,cs=np.unique(targs,return_counts=True)
    eachPersonCor={}
    eachPersonCount={}
    counter=0
    for n in ns:
        eachPersonCor[n]=0
        eachPersonCount[n]=float(cs[counter])
        counter+=1

    someys = bm.predict(td)
    for py,ay in zip(someys,targs):
        if(py==ay):
            eachPersonCor[ay]+=1
    for n in ns:
        print("Accuracy for "+ n+": %2.2f"%(eachPersonCor[n]/eachPersonCount[n]))

def doHTBasic(thechat):
    holdsAllMessages=np.array([])
    targets=np.array([])

    for c in thechat.users:
            
        holdsAllMessages = np.append(holdsAllMessages,thechat.users[c].cleanMessages)
        
        targets=np.append(targets,np.repeat(c,len(thechat.users[c].cleanMessages)))

    text_clf = Pipeline([
        ('vect', CountVectorizer()),
        ('tfidf', TfidfTransformer()),
        ('clf', MultinomialNB()),
    ])
    parameters = {
        'vect__ngram_range': [(1, 1), (1, 2),(1,3)],
        'tfidf__use_idf': (True, False),
        'clf__alpha': (1e-2, 1e-3,0.1,0.09),
    }
    somtin = GridSearchCV(text_clf, parameters, cv=5, iid=False, n_jobs=2,scoring='f1_macro')
    bestmodel = somtin.fit(holdsAllMessages,targets)
    return bestmodel,holdsAllMessages,targets

def multiClassAcc(model,datas):
    ns,cs=np.unique(datas[1],return_counts=True)
    eachPersonCor={}
    eachPersonCount={}
    counter=0
    for n in ns:
        eachPersonCor[n]=0
        eachPersonCount[n]=float(cs[counter])
        counter+=1
    x = datas[0]
    y = datas[1]
    someys = model.predict(x)
    for py,ay in zip(someys,y):
        if(py==ay):
            eachPersonCor[ay]+=1
    for n in ns:
        print("Accuracy for "+ n+": %2.2f"%(eachPersonCor[n]/eachPersonCount[n]))

def testAcc(model,datas):
    x = datas[0]
    y = datas[1]
    ovacc = 0
    someys = model.predict(x)
    for py,ay in zip(someys,y):
        if(py==ay):
            ovacc +=1
    print("Accuracy: "+str(ovacc/float(len(y))))

def tryBagOfWords(thechat,trainsplit = 0.8,bestModel=None):
    holdsAllTrainMessages=np.array([])
    holdsAllTestMessages=np.array([])
    targetsTrain=np.array([])
    targetsTest=np.array([])

    for c in thechat.users:
        #here we split into train and test
        mesSize = len(thechat.users[c].cleanMessages)
        trainInds = np.random.choice(mesSize, int(trainsplit*mesSize),replace=False).astype(int)
        testInds = np.setdiff1d(np.arange(mesSize),trainInds).astype(int)
        
        #pdb.set_trace()
        print(testInds)
            
        holdsAllTrainMessages = np.append(holdsAllTrainMessages,thechat.users[c].cleanMessages[trainInds])
        holdsAllTestMessages = np.append(holdsAllTestMessages,thechat.users[c].cleanMessages[testInds])
        
        targetsTrain=np.append(targetsTrain,np.repeat(c,len(trainInds)))
        targetsTest=np.append(targetsTest,np.repeat(c,len(testInds)))

    if(bestModel is None):
        count_vect = CountVectorizer(ngram_range=(1,2))
        alpha = 1
        doFreq = True
    else:
        ngram = bestModel.best_params_['vect__ngram_range']
        count_vect = CountVectorizer(ngram_range=ngram)
        doFreq = bestModel.best_params_['tfidf__use_idf']
        alpha = bestModel.best_params_['clf__alpha']

    X_train_counts = count_vect.fit_transform(holdsAllTrainMessages)
    X_test_counts = count_vect.transform(holdsAllTestMessages)
    tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)
    X_train_tf = tf_transformer.transform(X_train_counts)
    X_test_tf = tf_transformer.transform(X_test_counts)
      
    if(doFreq):
        xtrain = X_train_tf 
        xtest = X_test_tf
    else:
        xtrain = X_train_counts 
        xtest=X_test_counts
        
    clf = MultinomialNB(alpha=alpha).fit(xtrain, targetsTrain)
    return clf,(xtrain,targetsTrain),(xtest,targetsTest)
    
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

def startGroupMe(jsondata):
    userids=[]
    for n in jsondata:
        tusd = n["user_id"]
        if tusd not in userids:
            userids.append(tusd)
    return userids
def main():
    chowderPath ='/home/avanroi1/messages/inbox/chowder_g03zkk7sug'
    weirdPathName = '/home/avanroi1/messages/inbox/mualphanugammaomicron_baafcd34pg'
    groupmePathName = '/home/avanroi1/groupmeData/theboys'

    data = getJson(chowderPath)
    data = getJson(weirdPathName)
    gmdata = getJson(groupmePathName)
    gcids = startGroupMe(gmdata)
    args = parseArgs()
    numMessages = getNumMessages(data)
    username = args.username
    nameVec = data["participants"]
    print(nameVec)
    nameVec = [x['name'] for x in nameVec]
    #nameVec.append(username)
    if(debug is True):
        print(nameVec)
    c = Chat(nameVec,data)
    c2= Chat(gcids,gmdata,isGM=True)
    c2.popSelfDict()
    c2.updateUserStats()
    c2.printStats()
    if(doModel):
        bestmodel,data,targs = doHTBasic(c)
        model,train,test = tryBagOfWords(c,bestModel=bestmodel)

        #pdb.set_trace()
        whatevs = bestmodel.predict(["Miss you mangos"])
        print(whatevs)
        print(bestmodel.best_score_ )
        print(doPipeLineAcc(bestmodel,data,targs))
        print(bestmodel.best_params_)
        trainAcc = testAcc(model,train)
        trainAcc = testAcc(model,test)
        multiClassAcc(model,train)
        print("Test set results")

        multiClassAcc(model,test)
    #c.dumpChatStats()
main()
