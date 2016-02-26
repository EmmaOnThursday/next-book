import pdb
from model import User, Book, UserBook, BookSubject, Subject, Recommendation, db, connect_to_db
from server import app
import pandas as pd 
import numpy as np 
from datetime import datetime

user_id = 1

connect_to_db(app)

# import necessary data from db
library = pd.read_sql_table('library', 
    con='postgres:///nextbook',
    columns=['book_id', 'title', 'author', 'pub_year', 'original_pub_year', 'pages'])

book_subjects = pd.read_sql_table('book_subjects', 
    con='postgres:///nextbook')

subjects = pd.read_sql_table('subjects', con='postgres:///nextbook', 
    columns=['subject_id', 'subject'])

user_ratings = pd.read_sql_query(sql=('SELECT book_id, user_id, status, rating FROM user_books WHERE user_id=%s' % user_id), 
    con='postgres:///nextbook')

# merge user ratings into library
library = library.merge(user_ratings, how='left', on='book_id')
library['pages'].fillna(0, inplace=True)


# merge subject names into book_subjects; drop uninteresting subjects from all tables
book_subjects = book_subjects.merge(subjects, how='left', on='subject_id')
delete_values = ["protected daisy", "accessible book", "in library", "overdrive", "large type books", 'ficci\xc3\xb3n juvenil', 'ficci\xc3\xb3n', 'lending library']
book_subjects = book_subjects[~book_subjects['subject'].isin(delete_values)]


# group by book ids
book_lists = book_subjects.groupby('book_id')
books = book_subjects['book_id']

# create dictionary of all books + associated subjects
books_with_subject_lists = {}
for book_id in books:
    subjects = []
    for subj in book_lists.get_group(book_id)['subject']:
        if books_with_subject_lists.get(book_id):
            books_with_subject_lists[book_id].append(subj)
        else:
            books_with_subject_lists[book_id] = [subj]

# dictionary becomes a data frame; rename columns
books_with_subjects = pd.DataFrame(books_with_subject_lists.items())
books_with_subjects.columns = ['book_id', 'subjects']

# merge subject lists into library
book_attributes = library.merge(books_with_subjects, how='left', on='book_id')
book_attributes['subjects'] = book_attributes['subjects'].fillna("")

# create a list of common subjects; check if each subject in each book's subject list
def get_common_subjects(book_subjects):
    common_subjects = []
    all_subj = list(book_subjects['subject'])
    for subject in book_subjects['subject']:
        if all_subj.count(subject) > 14:
            common_subjects.append(subject)

    return common_subjects #list of common subject names

common_subjects = get_common_subjects(book_subjects)

for subject in common_subjects:
    subj_column = []
    for x in book_attributes['subjects']:
        if subject in x:
            subj_column.append(1)
        else:
            subj_column.append(0)
    book_attributes[subject] = subj_column


# for date columns: dates > date categories > binary columns 
def transform_pub_dates(column):
    date_categories = []
    for item in column:
        if item > 1950:
            date_categories.append('1950+')
        elif item > 1900:
            date_categories.append('1901-50')
        elif item > 1850:
            date_categories.append('1851-1900')
        elif item > 1800:
            date_categories.append('1851-1900')      
        elif item > 1700:
            date_categories.append('1701-1800')      
        elif item > 1500:
            date_categories.append('1501-1700')  
        else:
            date_categories.append('Unknown')    
    
    return date_categories
    
# insert date_categories into data frame
orig_pub_year_cat = transform_pub_dates(book_attributes['original_pub_year'])
book_attributes.insert(loc=5, column='orig_pub_year_cat', value=orig_pub_year_cat)

pub_year_cat = transform_pub_dates(book_attributes['pub_year'])    
book_attributes.insert(loc=5, column='pub_year_cat', value=pub_year_cat)

# turn date categories into binary dataframes; merge back into book_attributes
pub_year_dummies = pd.get_dummies(book_attributes['pub_year_cat'])
orig_year_dummies = pd.get_dummies(book_attributes['orig_pub_year_cat'])

book_full_attr = book_attributes.merge(pub_year_dummies,left_index=True, right_index=True)
book_full_attr = book_full_attr.merge(orig_year_dummies,left_index=True, right_index=True)

# move rating column to index 0:
rating_list = book_full_attr['rating']
book_full_attr = book_full_attr.drop('rating', 1)
book_full_attr.insert(loc=0, column='ratings', value=rating_list)


# drop non-numeric columns; create dfs for fit & prediction
books_for_prediction = book_full_attr.drop(['subjects', 'status', 'user_id'], 1)
rated = books_for_prediction[books_for_prediction['ratings'].isin([1,2,3,4,5])]
to_rate = books_for_prediction[~books_for_prediction['ratings'].isin([1,2,3,4,5])]

print "created train & predict DFs"

# PREDICTIONS
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cross_validation import KFold
import random


# define random train & validate sets
rows = random.sample(rated.index, 209)
rated_train = rated.ix[rows[:160]]
rated_validate = rated.ix[rows[160:]]


# run Random Forest
rf = RandomForestClassifier(n_estimators=50)
rf.fit(rated_train.iloc[:,8:], rated_train.iloc[:, 0])
rf_predictions = rf.predict(rated_validate.iloc[:,8:])

print "rf run complete"

# run kNN
neighbors = KNeighborsClassifier(n_neighbors=11)
neighbors.fit(rated_train.iloc[:,8:], rated_train.iloc[:, 0])
knn_predictions = neighbors.predict(rated_validate.iloc[:,8:])

print "knn run complete"

# ACCURACY

# get & save validation ratings
actuals = rated_validate['ratings']

# categorizing do/do not recommend ratings
def rating_categories(rating_list):
    ratings = []
    for x in rating_list:
        if x > 3:
            ratings.append(1)
        else:
            ratings.append(-1)
    return ratings

# Categorize ratings to do/do not recommend
rf_recommendations = rating_categories(rf_predictions)
actual_ratings = rating_categories(actuals)
knn_recommendations = rating_categories(knn_predictions)

# accuracy calculation for algorithm comparison
def calculate_accuracy(validation_ratings, predicted_ratings):
    correct = 0
    for x, y in zip(validation_ratings, predicted_ratings):
        if x==y:
            correct +=1
    accuracy = correct/float(len(validation_ratings))
    return accuracy

rf_accuracy = calculate_accuracy(actual_ratings, rf_recommendations)

knn_accuracy = calculate_accuracy(actual_ratings, knn_recommendations)

if rf_accuracy > knn_accuracy:
    print "RF wins with accuracy of", rf_accuracy
elif knn_accuracy > rf_accuracy:
    print "kNN wins with accuracy of", knn_accuracy
else:
    print "maybe a tie? check your results"

def get_best_predictor():
    if rf_accuracy >= knn_accuracy:
        return rf
    elif knn_accuracy > rf_accuracy:
        return neighbors


# GET ACTUAL PREDICTIONS
model = get_best_predictor()

model_predictions = model.predict(to_rate.iloc[:,8:])
model_recommendations = rating_categories(model_predictions)

to_rate['recommendations'] = model_recommendations
to_rate['predicted_ratings'] = model_predictions

to_recommend = to_rate[to_rate['recommendations']==1]

def add_predictions_to_database(dataframe):
    for i, row in dataframe.iterrows():
        new_userbook = UserBook(user_id=user_id, 
            source = "nextbook-rec",
            status = "rec_no_response",
            book_id= row['book_id'])
        db.session.add(new_userbook)
    db.session.flush()
    
    for i, row in dataframe.iterrows():
        current_userbook = UserBook.query.filter(UserBook.book_id==row['book_id'], 
            UserBook.user_id==user_id).first()
        new_recommendation = Recommendation(date_created=datetime.now(), 
            userbook_id=current_userbook.userbook_id)
        db.session.add(new_recommendation)

    db.session.commit()

add_predictions_to_database(to_recommend)


def create_recommendations(dataframe):
    """Add recommendations to database. """
    recs_created = 0
    for i, row in dataframe.iterrows():
        current_userbook = UserBook.query.filter(UserBook.book_id==row['book_id'], UserBook.user_id==user_id).first()
        new_recommendation = Recommendation(date_created=datetime.now(), userbook_id=current_userbook.userbook_id)
        db.session.add(new_recommendation)
        recs_created += 1
    db.session.commit()

    return recs_created

def user_alert(new_recs):
    if new_recs > 0:
        # send email to user saying recommendations are complete
        print "New recs added to DB:", new_recs
    else:
        # email nextbook recommends  with error message
        print "no recs created for this user"

new_recs = create_recommendations(to_recommend)
user_alert(new_recs)


