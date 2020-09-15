# Importing libraries
import keras
from keras.datasets import imdb
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense, Flatten, Dropout, Activation, Embedding, Conv1D, GlobalMaxPool1D, SpatialDropout1D
from keras.callbacks import ModelCheckpoint
import os
import sklearn.metrics
from sklearn.metrics import roc_auc_score

# variables:

output_dir = 'imdb/deep_net'
epochs = 4
batch_size = 128
n_dim = 64
n_unique_words = 5000
n_words_to_skip = 50
max_review_length = 100
pad_type = trunc_type = 'pre'
n_dense= 64
dropout=0.5
drop_embed = 0.2
n_conv = 256
k_conv = 3

(x_train, y_train), (x_valid, y_valid) = imdb.load_data(num_words=n_unique_words, skip_top=n_words_to_skip)

for x in x_train[0:6]:
    print(len(x))

word_index=keras.datasets.imdb.get_word_index()

for n,k in word_index.items():
    if k ==2:
        print(n)

word_index = {k:v+3 for k,v in word_index.items()}


word_index['PAD'] = 0
word_index['START'] = 1
word_index['UNK'] = 2


def index_word(k):
    for n, o in word_index.items():
        if o==k:
            return n

review = ' '.join(index_word(k) for k in x_train[0])

(all_X_train, _), (all_X_valid, _) = imdb.load_data()
full_review = ' '.join(index_word(l) for l in all_X_train[0])
print(full_review)


x_train = pad_sequences(x_train, maxlen=max_review_length, padding=pad_type, truncating=trunc_type, value=0 )
x_valid = pad_sequences(x_valid, maxlen=max_review_length, padding=pad_type, truncating=trunc_type, value=0 )


for x in x_train[0:6]:
    print(len(x))


review = ' '.join(index_word(k) for k in x_train[0])

# Using Deep Neural Network

model = Sequential()
model.add(Embedding(n_unique_words, n_dim, input_length=max_review_length))
model.add(Flatten())
model.add(Dense(n_dense, activation='relu'))
model.add(Dropout(dropout))
model.add(Dense(1, activation='sigmoid'))

model.summary()

modelcheckpoint = ModelCheckpoint(filepath=output_dir + '\weights{epoch:02d}.hdf5')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, verbose=1, validation_split=0.2, 
         callbacks=[modelcheckpoint])


y_hat = model.predict_proba(x_valid)


pct_auc = roc_auc_score(y_valid, y_hat) * 100
print('{:0.2f}'.format(pct_auc))


# using convolutional neural network

modelc=Sequential()
modelc.add(Embedding(n_unique_words, n_dim, input_length=max_review_length))
modelc.add(SpatialDropout1D(drop_embed))
modelc.add(Conv1D(n_conv, k_conv, activation='relu'))
modelc.add(GlobalMaxPool1D())
model.add(Dense(n_dense, activation='relu'))
model.add(Dropout(dropout))
model.add(Dense(1, activation='sigmoid'))

model.compile(loss='binary_crossentropy', optimizer='adam',
    metrics=['accuracy'])

model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, 
    verbose=1, validation_split=.20,
    callbacks=[modelcheckpoint])

yc_hat = model.predict_proba(x_valid)
pct_auc = roc_auc_score(y_valid, yc_hat) * 100
print('{:0.2f}'.format(pct_auc))
