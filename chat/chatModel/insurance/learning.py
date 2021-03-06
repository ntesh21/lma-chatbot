# things we need for NLP
import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

# things we need for Tensorflow
import numpy as np
import tflearn
import tensorflow as tf
import random

# restore all of our data structures
import pickle

data = pickle.load( open( "chat/training_data3", "rb" ) )

words = data['words']
classes = data['classes']
train_x = data['train_x']
train_y = data['train_y']

# import our chat-bot intents file
import json
with open('chat/insurance.json') as json_data:
	intents = json.load(json_data)

# Build neural network
net = tflearn.input_data(shape=[None, len(train_x[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
# net = tflearn.lstm(net, 8, dropout=0.8, dynamic=True)
net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
net = tflearn.regression(net)

# Define model and setup tensorboard
model = tflearn.DNN(net, tensorboard_dir='tflearn_logs')

def clean_up_sentence(sentence):
    # tokenize the pattern
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence
def bow(sentence, words, show_details=False):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)

    return(np.array(bag))

p = bow("is your shop open today?", words)
print(p)
print(classes)

# load our saved model
model.load('chat/model3.tflearn')
# create a data structure to hold user context
# context = {}

ERROR_THRESHOLD = 0.20

def classify(sentence):
    # generate probabilities from the model
    results = model.predict([bow(sentence, words)])[0]
    # filter out predictions below a threshold
    results = [[i,r] for i,r in enumerate(results) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)

    return_list = []
    for r in results:
        # return_cata.append((category[r[0]]))
        return_list.append((classes[r[0]], r[1]))
    # return tuple of intent and probability
    return return_list

def response(sentence, userID='123', show_details=False):
    
    results = classify(sentence)
    print(results[0][1])
    # if we have a classification then find the matching intent tag
    if results:
        # loop as long as there are matches to process
        while results:
            for i in intents['intents']:
                # find a tag matching the first result
                if i['intention'] == results[0][0]:
                    reply = i['reply']
                    answer = reply[0]
                     if results[0][1]<0.85:
                        return "Sorry, I do not understand you"
                    else:
                        return answer
        results.pop(0)


   
#print('Bot:Welcome, Let me help you with all the information you want to know about our restaurants')
#while 1:
    #query = input("You:")
    #c = (classify(query))
    #r = c[0][1]
    #print(r)



    #if query=='goodbye':
        #print('Thank you for visiting!')
        #break
    #if r<0.85:
        #print("Sorry, I do not understand you")
    #else:
        #response(query)
