import os
import json
import argparse
import sys
import pdb
import numpy as np

debug = False

def getJson(pathName):
    if(debug is True):
        print(os.getcwd())
        print(os.listdir('/home/avanroi1/messengerData/testData/MuAlphaNuGammaOmicron_34ea4e8c3b'))

    with open(pathName+'/message.json') as f:
        data = json.load(f)

    return data
    

def main():
    boysPath ='/home/avanroi1/groupmeData/theboys'
    data = getJson(boysPath)
    pdb.set_Trace()
    
main()