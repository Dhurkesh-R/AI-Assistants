# import nltk
# from nltk.stem.lancaster import LancasterStemmer
# Stemmer = LancasterStemmer()

# import nltk
# nltk.download('punkt')

# import numpy
# import tensorflow
# import tflearn
# import random
# import json

# with open("intents.json") as file:
#     data = json.load(file)

# words = []
# labels = []
# docs_x = []
# docs_y = []

# for intent in data['intents']:
#     for pattern in intent['patterns']:
#         wrds = nltk.word_tokenize(pattern)
#         words.extend(wrds)
#         docs_x.append(wrds)
#         # Append the tag from the current intent to docs_y
#         docs_y.append(intent['tag'])

#     if intent['tag'] not in labels:
#         labels.append(intent['tag'])

# words = [Stemmer.stem(w.lower()) for w in words if w != '?']
# words = sorted(list(set(words)))

# labels = sorted(labels)

# training = []
# output = []

# out_empty = [0 for _ in range(len(labels))]

# for x, doc in enumerate(docs_x):
#     bag = []

#     wrds = [Stemmer.stem(w.lower()) for w in doc]

#     for w in words:
#         if w in wrds:
#             bag.append(1)
#         else:
#             bag.append(0)

#     output_row = out_empty[:]
#     # Get the tag for the current intent
#     tag = docs_y[x]
#     output_row[labels.index(tag)] = 1

#     training.append(bag)
#     output.append(output_row)


# training = numpy.array(training)
# output = numpy.array(output)

# tensorflow.reset_default_graph()

# net = tflearn.input_data(shape=[None, len(training[0])])
# net = tflearn.fully_connected(net, 8)
# net = tflearn.fully_connected(net, 8)
# net = tflearn.fully_connected(net, len(output[0]), activation= 'softmax')
# net = tflearn.regression(net)

# model = tflearn.DNN(net)

# model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)

# model.save('Stark Bot')

import warnings

# Suppress FutureWarnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

import numpy
import tflearn
import tensorflow as tf
import random
import json
import pickle

with open("intents.json") as file:
    data = json.load(file)

try:
    with open("data.pickle", "rb") as f:
        words, labels, training, output = pickle.load(f)
except (FileNotFoundError, EOFError):
    words = []
    labels = []
    docs_x = []
    docs_y = []
    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent["tag"])
        if intent["tag"] not in labels:
            labels.append(intent["tag"])
    ignore_words = ['!', '?', '.', ',']
    words = [stemmer.stem(w.lower()) for w in words if w not in ignore_words]
    words = sorted(list(set(words)))
    labels = sorted(labels)
    training = []
    output = []
    out_empty = [0 for _ in range(len(labels))]
    for x, doc in enumerate(docs_x):
        bag = []
        wrds = [stemmer.stem(w.lower()) for w in doc]
        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)
        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1
        training.append(bag)
        output.append(output_row)
    training = numpy.array(training)
    output = numpy.array(output)
    with open("data.pickle", "wb") as f:
        pickle.dump((words, labels, training, output), f)
# Adjusting the permissions of the file
os.chmod("data.pickle", 0o666)

tf.reset_default_graph()

net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)

model = tflearn.DNN(net)

model_file = 'C:/Users/Dhurkesh/ML learner/ChatBots/model.tflearn'

# def load_model():
#     try:
#         # Attempt to load the model
#         model = tf.keras.models.load_model(model_file)
#         print("Model loaded successfully!")
#         return model
#     except Exception as e:
#         print("Error loading the model:", e)
        # return None

try:
    model.load("model.tflearn")
except (FileNotFoundError, tf.errors.NotFoundError):
    model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
    model.save("model.tflearn")

def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1
            
    return numpy.array(bag)


def chat():
    print("Start talking with the Stark bot (type quit to stop)!")
    while True:
        inp = input("You: ")
        if inp.lower() == "quit":
            break

        results = model.predict([bag_of_words(inp, words)])
        results_index = numpy.argmax(results)
        confidence = results[0][results_index]

        bot_name = "Tony"

        if confidence > 0.8:
            tag = labels[results_index]
            for intent in data["intents"]:
                if intent["tag"] == tag:
                    responses = intent["responses"]
            print(f"{bot_name}: {random.choice(responses)}")
        else:
            print(f"{bot_name}: I didn't get that, please try again.")

chat()

