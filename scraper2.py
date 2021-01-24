from newspaper import Article
import nltk
import pandas as pd

nltk.download('punkt')

url = 'https://www.scmp.com/coronavirus'
article = Article(url, language="en") # en for English
'''
titleList = []
testList = []
summaryList = []
keyList = []
'''
article.download()
article.parse()
article.nlp()

print('\n'+ article.title + '\n') #prints the title of the article

'''
print("Article Text:")
print(article.text) #prints the entire text of the article
print("\n")
print("Article Summary:")
print(article.summary) #prints the summary of the article
print("\n")
print("Article Keywords:")
print(article.keywords) #prints the keywords of the article
'''

points = article.summary.split('.')
print(points)


#for point in points:
#    with open(r'C:\Users\saura\Documents\ML2021\NewsScraper\output.txt', 'w') as file_object:
#        file_object.write(point)



#### SENTIMENT ANALYSIS ####

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import pandas as pd
from tensorflow import keras
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM,Dense,Dropout
from tensorflow.keras.layers import SpatialDropout1D
from tensorflow.keras.layers import Embedding

#import speech_recognition as sr
# Loading model
reconstructed_model = keras.models.load_model('./models')

text = "UK MP devastated that coronavirus isn't infecting more people"


df= pd.read_csv('Tweets.csv', sep=',')

#select relavant columns
tweet_df = df[['text','airline_sentiment']]
tweet_df = tweet_df[tweet_df['airline_sentiment'] != 'neutral'] #filtering out neutral comments

# convert airline_seentiment to numeric
sentiment_label = tweet_df.airline_sentiment.factorize()  # positive:0,negative:1

# Setting up word embeddings
tweet = tweet_df.text.values
tokenizer = Tokenizer(num_words=5000)
tokenizer.fit_on_texts(tweet)
vocab_size = len(tokenizer.word_index) + 1
encoded_docs = tokenizer.texts_to_sequences(tweet)
padded_sequence = pad_sequences(encoded_docs, maxlen=200)

def return_df():
    return_df = pd.DataFrame(columns=['Heading','Sentiment'])

    for text in points:
        test_word = text
        tw = tokenizer.texts_to_sequences([test_word])
        tw = pad_sequences(tw, maxlen=200)
        prediction = int(reconstructed_model.predict(tw).round().item())
        return_df = return_df.append(pd.DataFrame([[text,prediction]],columns=['Heading','Sentiment']))
        return_df = return_df.replace({'Sentiment': {1:'Negative',0:'Positive'}})

    print(return_df)

    return return_df



# Model Training
