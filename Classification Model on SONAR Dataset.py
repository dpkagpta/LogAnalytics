
import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import cross_val_score


aset = pd.read_csv(r'E:\My_Training\Bboks\sonar.all-data.csv', header=None)
dataset= dataset.values

X= dataset[:, 0:60].astype(float)
y= dataset[:, 60]


seed=7
np.random.seed(seed)
encoder=LabelEncoder()
encoder.fit(y)
coded_y= encoder.transform(y)


def create_baseline():
    model=Sequential()
    model.add(Dense(60, input_dim=60, kernel_initializer='uniform', activation='relu'))
    model.add(Dense(1, kernel_initializer='uniform', activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model


estimator= KerasClassifier(build_fn=create_baseline, epochs=150, batch_size=5, verbose=0)
kfold= StratifiedKFold(n_splits=10, shuffle=True, random_state=seed)

results=cross_val_score(estimator, X, coded_y, cv= kfold, verbose=0)

print("%.2f%% (+- %.2f%%)" % (results.mean()*100, results.std()*100))


# training while standardizing

from sklearn.pipeline import Pipeline
estimators = []
estimators.append(('standardize', StandardScaler()))
estimators.append(('mlp', KerasClassifier(build_fn=create_baseline, epochs=150, batch_size=5, verbose=0)))
pipeline= Pipeline(estimators)
kfold=StratifiedKFold(n_splits=10, shuffle=True, random_state=seed)
results = cross_val_score(pipeline, X, coded_y, cv=kfold)

print("%.2f%% (+- %.2f%%)" % (results.mean()*100, results.std()*100))
