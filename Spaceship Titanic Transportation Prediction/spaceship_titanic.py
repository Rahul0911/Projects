# -*- coding: utf-8 -*-

#**SPACESHIP TITANIC COMPETITION**

Data Source: https://www.kaggle.com/competitions/spaceship-titanic/code
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV
from xgboost import XGBClassifier
import lightgbm as lgbm
from sklearn.ensemble import StackingClassifier
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold


def datacleaning(train_path, test_path):
  train = pd.read_csv(train_path)
  test = pd.read_csv(test_path)

  #Dropping the unnecessary columns from training and testing dataset
  train1 = train.drop(['PassengerId', 'Cabin', 'Name'], axis=1)
  test1 = test.drop(['PassengerId', 'Cabin', 'Name'], axis=1)

  #Encoding the categorical features to convert them into numerical features
  le = LabelEncoder()
  columns_to_convert_tr = ['HomePlanet', 'CryoSleep', 'Destination', 'VIP', 'Transported']
  columns_to_convert_ts = ['HomePlanet', 'CryoSleep', 'Destination', 'VIP']

  for i in columns_to_convert_tr:
    train1[i] = le.fit_transform(train[i])

  for j in columns_to_convert_ts:
    test1[j] = le.fit_transform(test1[j])

  #Imputing the missing values in the columns with the mean of the columns
  impute = SimpleImputer(strategy='mean')
  cols_to_impute = ['Age', 'RoomService', 'FoodCourt', 'ShoppingMall', 'Spa', 'VRDeck']

  train1[cols_to_impute] = impute.fit_transform(train1[cols_to_impute])
  test1[cols_to_impute] = impute.transform(test1[cols_to_impute])

  #Scaling the columns with large data values
  scaler = MinMaxScaler()
  cols_to_scale = ['Age', 'RoomService', 'FoodCourt', 'ShoppingMall', 'Spa', 'VRDeck']

  train1[cols_to_scale] = scaler.fit_transform(train1[cols_to_scale])
  test1[cols_to_scale] = scaler.transform(test1[cols_to_scale])

  #splitting the training data into train test split
  X = train1.drop(['Transported'], axis=1)
  y = train1['Transported']

  #X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=69)

  return X, y, test1


def evaluate_model(model, X, y):
    cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=69)
    scores = cross_val_score(model, X, y, scoring='accuracy', cv=cv, n_jobs=-1, error_score='raise')
    return scores


def main():
  train_path = '/content/train_space.csv'
  test_path = '/content/test_space.csv'

  X, y, test1 = datacleaning(train_path, test_path)

  rf = RandomForestClassifier(n_estimators=100, max_features='sqrt', max_depth=8, min_samples_split=10, bootstrap=True)
  lr = LogisticRegression(C=10, penalty='l2')
  svm = SVC(C=10, kernel='linear')
  xgb = XGBClassifier()
  lgb = lgbm.LGBMClassifier(num_leaves=15, max_depth=-1, random_state=1, silent=True, metric='None',
                                  n_jobs=4, n_estimators=1000, max_iter=10, colsample_bytree=0.9, subsample=0.9, learning_rate=0.1)

  estimators = [('rf',rf), ('lr',lr),('svm',svm),('xgb',xgb),('lgb',lgb)]

  stacking_model = StackingClassifier(estimators=estimators,
                                      final_estimator= lr,
                                      cv=5)

  algo = 'Stacking Classifer'
  scores = evaluate_model(stacking_model, X, y)
  print(f"Algorithm {algo}'s Accuracy >>> {np.mean(scores)}")


if __name__ == "__main__":
    main()