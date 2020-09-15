# Let's start with importing all the required libraries 

import numpy as np
import pandas as pd
import tensorflow as tf
import seaborn as sns
import keras
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegressionCV
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers.core import Dense, Activation
from sklearn.metrics import classification_report,confusion_matrix


print(sklearn.__version__)
print(keras.__version__)
print(tf.__version__)


# Loading the data
iris = sns.load_dataset('iris')
iris.head()


# Visualize the data to have a clear understanding
v = sns.pairplot(iris, hue = 'species')


# Preparing our dataset for training
X = iris[iris.columns.difference(['species'])]
y = iris['species']
train_X, test_X, train_y, test_y = train_test_split(X, y, random_state = 0, test_size = 0.5)


# Training using Scikit-learn
lr = LogisticRegressionCV(cv = 3, multi_class = 'ovr')
lr.fit(train_X, train_y)
pred_y = lr.predict(test_X)
print('The accuracy achieved by this model is {:.2f}'.format(lr.score(test_X, test_y)))


# Training using Keras
def onehotencode(arr):
    uniques, ids = np.unique(arr, return_inverse = True)
    return np_utils.to_categorical(ids, len(uniques))

encoded_train_y = onehotencode(train_y)
encoded_test_y = onehotencode(test_y)


# Creating a model
model = Sequential()
model.add(Dense(10, input_dim=4, activation='relu'))
model.add(Dense(10, activation='relu'))
model.add(Dense(3, activation='softmax'))

# Compiling model
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Training the model
model.fit(train_X, encoded_train_y, epochs=500, batch_size=10)


# Evaluating it:
scores = model.evaluate(test_X, encoded_test_y)
print("\nAccuracy: %.2f%%" % (scores[1]*100))



# Creating another model in Keras
def baseline_model():
    model=Sequential()
    model.add(Dense(4, input_dim=4, kernel_initializer='normal', activation='relu'))
    model.add(Dense(3, kernel_initializer='normal', activation='sigmoid'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model



estimator=KerasClassifier(build_fn=baseline_model, epochs=150, batch_size=5, verbose=0)
kfold = KFold(n_splits=10, shuffle=True, random_state=seed)

results= cross_val_score(estimator, X, dummy_y, cv=kfold)

print("%.2f%% (+- %.2f%%)" % (results.mean()*100, results.std()*100))


kfold = StratifiedKFold(n_splits=10, shuffle=True, random_state=seed)
cvscores = []
for train, test in kfold.split(X, y):
        model= Sequential()
        model.add(Dense(12, input_dim = 8, kernel_initializer='uniform', activation='relu'))
        model.add(Dense(8, kernel_initializer='uniform', activation='relu'))
        model.add(Dense(1, kernel_initializer='uniform', activation='sigmoid'))
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy']) 
        model.fit(X[train], y[train], epochs=150, batch_size=10, verbose=0)  
        scores=model.evaluate(X[test], y[test], verbose=0)  
        cvscores.append(scores[1]*100)


print("%.2f%% (+- %.2f%%)" % (results.mean()*100, results.std()*100))

def create_model():
    model= Sequential()
    model.add(Dense(12, input_dim = 8, kernel_initializer='uniform', activation='relu'))
    model.add(Dense(8, kernel_initializer='uniform', activation='relu'))
    model.add(Dense(1, kernel_initializer='uniform', activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy']) 
    return model

model = KerasClassifier(build_fn=create_model, epochs = 150, batch_size=10,verbose=0)
kfold= StratifiedKFold(n_splits=10, shuffle=True,random_state=seed)

results=cross_val_score(model, X, y, cv=kfold)


print("%.2f%% (+- %.2f%%)" % (results.mean()*100, results.std()*100))