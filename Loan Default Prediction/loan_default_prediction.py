# -*- coding: utf-8 -*-
"""Loan Default Prediction

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1X2GpJfm0KlmQUTsgu3rkYhXtUmqP_hRr

#**Using the LightGBM algorithm to predict the default cases**

Dataset Source: https://www.kaggle.com/datasets/nikhil1e9/loan-default
"""

#Importing the important libraries
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#Reading the dataset
data = pd.read_csv('/content/Loan_default.csv')

#Reading the first 5 rows of the dataset to get familiar with the type of information with the dataset
data.head()

#Printing information about the dataframe
data.info()

#Checking if the data has any missing values
data.isnull().sum()

#Checking the number of unique values in the categorical feature with cardinality more than 2
temp = data[['Education', 'EmploymentType', 'MaritalStatus', 'LoanPurpose']].nunique()
temp

#Splitting the dependent (y) and independent (X) features
X = data.drop(['LoanID', 'Default'], axis =1)
y= data['Default']

#Converting the categorical feature into appropriate type for the LightGBM
for i in X.columns:
  column_type = X[i].dtype
  if column_type == 'object' or column_type.name == 'category':
    X[i] = X[i].astype('category')

#Printing information about the independent feature after changing the dtypes of categorical feature from 'object' to 'category'
X.info()

#Splitting the data into training and test set
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state=1)

#Importing the LightGBM algorithm
import lightgbm as lgbm
classifier = lgbm.LGBMClassifier(num_leaves=15, max_depth=-1, random_state=1, silent=True, metric='None',
                                 n_jobs=4, n_estimators=1000, colsample_bytree=0.9, subsample=0.9, learning_rate=0.1)

#Training the model
classifier.fit(X_train, y_train)

#Plotting the feature importance graph according to out LightGBM model
feat_imp = pd.Series(classifier.feature_importances_, index=X.columns)
feat_imp.nlargest(20).plot(kind='barh', figsize=(8,10))

"""##Observation
As we can see that our LightGBM algorthm thinks of **Credit Score** as the most important feature in predicting the default case followed by Loan Amount and Interest rate of the loan whereas **Education** is the least important feature when it comes to replayment of the loan.
"""

#Predicting the defaulters based on our test data
y_pred = classifier.predict(X_test)

#Checking the accuracy of our trained model
from sklearn.metrics import accuracy_score
accuracy=accuracy_score(y_pred, y_test)

print('Accuracy using LightGBM algorithm: ',accuracy)

"""#**Comparing the accuracy of LighGBM with other classification algorithms**"""

#Making a copy of the original dataset
dataset = data.copy()
dataset.head()

#Using label encoder to convert the categorical features into numerical form
from sklearn.preprocessing import LabelEncoder
encoder = LabelEncoder()
category_col = ['HasCoSigner','LoanPurpose','HasDependents', 'HasMortgage','MaritalStatus', 'EmploymentType', 'Education']

for i in category_col:
  dataset[i] = encoder.fit_transform(dataset[i])

dataset = dataset.drop(['LoanID'], axis=1)

#Checking the data type of features after the label encoder operartion
dataset.dtypes

#Now that all the categorical columns are converted into numerical columns, lets check there correlation with the target feature
featurecorr = dataset.corr()['Default'].sort_values()
featurecorr

"""###Observation
As we can see interest rate has a high positive correlation to the Default cases which was not the case in the lightGBM model. For lightGBM model Credit Score was the most important feature
"""

#Lets try to implement the result above in a more visually appealing form
import plotly.express as px
fig = px.imshow(dataset.corr(), text_auto=True)
fig.update_layout(
    autosize=False,
    width=1100,
    height=1100,)
fig.show()

"""##Insights from the heatmap
As we can see in the heat map, Age is negatively correlated to the default cases, which is still important as it tells us about the patterns related to this two features, for example younger the person, higher is the chance of them defaulting a loan. Where as Interest rate is postively correlated to the Default cases which tells is that, higher the interest rate of a loan, higher is the chance for a person to default that loan. Lets see it in a more visually appealing form below.
"""

sns.lineplot(data= dataset, x = 'Age', y= 'Default')

sns.lineplot(data= dataset, x = 'InterestRate', y= 'Default')

#Splitting the data into dependent and independent features
X1 = dataset.drop(['Default'], axis=1)
y1 = dataset['Default']

#Splitting the data into train and test dataset
X1_train, X1_test, y1_train, y1_test = train_test_split(X1, y1, test_size=0.2, random_state=1)

#Importing multiple classification algorithms
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from xgboost import XGBClassifier

models = [
  XGBClassifier(),
  RandomForestClassifier(),
  LogisticRegression(),
  KNeighborsClassifier(),
]

for mod in models:
  mod.fit(X1_train, y1_train)
  y_pred1 = mod.predict(X1_test)
  score = accuracy_score(y_pred1, y1_test)
  model_name = mod.__class__.__name__
  print(f'{model_name} -> Accuracy: {score: .2f}')

"""##Observation
As we can see, XGBoost and RandomForest algorithms worked even better than LightGBM algorithm, followed by Logistic Regression which performed same as the LightGBM whereas KNeighbors performed the worst out of all these algorithms.

Even though we had to do some data preprocessing with the categorical features to get a good accuracy with XGBoot and RandomForest, LightGBM performed almost as good without even manipulating the categorical features.

This begs the question that, when the dataset is not clean at all (since I was lucky enough to get a clean dataset this time) and there are lots of categorical features, should be try to encode them and create lots of additional fetaures at the risk of overfitting OR should we let LightGBM algorithm to handle that on its own with just necessary data preprocessing steps.
"""