import pdb
from model import User, Book, UserBook, BookSubject, Subject, Recommendation, db
import pandas as pd 
import numpy as np 
from datetime import datetime, date

from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cross_validation import KFold
import random



### HELPER FUNCTIONS ###

def import_data_from_psql(user_id):
    """Import data from psql; clean & merge DFs."""    
    library = pd.read_sql_table('library', 
        con='postgres:///nextbook',
        columns=['book_id', 'title', 'author', 'pub_year', 'original_pub_year', 'pages'])

    book_subjects = pd.read_sql_table('book_subjects', 
        con='postgres:///nextbook')

    subjects = pd.read_sql_table('subjects', con='postgres:///nextbook', 
        columns=['subject_id', 'subject'])

    user_ratings = pd.read_sql_query(sql=('SELECT book_id, user_id, status, rating FROM user_books WHERE user_id=%s' % user_id), 
        con='postgres:///nextbook')

    library = library.merge(user_ratings, how='left', on='book_id')
    library['pages'].fillna(0, inplace=True)

    # merge subject names into book_subjects; drop uninteresting subjects from book_subjects table
    book_subjects = book_subjects.merge(subjects, how='left', on='subject_id')
    delete_values = ["protected daisy", "accessible book", "in library", "overdrive", "large type books", 'ficci\xc3\xb3n juvenil', 'ficci\xc3\xb3n', 'lending library']
    book_subjects = book_subjects[~book_subjects['subject'].isin(delete_values)]

    return [library, book_subjects, subjects]


def add_book_subjects_to_library(book_subjects, library):
    """Given clean book_subjects DF, add subjects for each book to library."""

    # group by book ids; create list of book_ids
    book_lists = book_subjects.groupby('book_id')

    # create dictionary of all books + associated subjects
    books_with_subject_lists = {}
    for book_id in book_subjects['book_id']:
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

    return book_attributes


def get_common_subjects(book_subjects):
    """Get list of all subjects associated with 15+ books."""

    #NOTES FOR REFACTORING:
        # using count makes for long runtime; maybe build a dictionary instead?
    common_subjects = []
    all_subj = list(book_subjects['subject'])
    for subject in book_subjects['subject']:
        if all_subj.count(subject) > 14:
            common_subjects.append(subject)

    return common_subjects #list of common subject names


def create_subject_columns(common_subjects, book_attributes):
    """For each subject in common_subjects, create a binary column in book_attributes."""
    for subject in common_subjects:
        subj_column = []
        for x in book_attributes['subjects']:
            if subject in x:
                subj_column.append(1)
            else:
                subj_column.append(0)
        book_attributes[subject] = subj_column
    return book_attributes



def transform_pub_dates(column):
    """Transform column of raw dates to column of bucketed date categories."""

    # look into rebinning these by population sizes?

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


def make_date_columns_categorical_binary(book_attributes):
    """Turn all date columns in book_attributes into binary categorical columns."""

    # bucket publish dates & insert categorical data columns into data frame
    orig_pub_year_cat = transform_pub_dates(book_attributes['original_pub_year'])
    book_attributes.insert(loc=5, column='orig_pub_year_cat', value=orig_pub_year_cat)

    pub_year_cat = transform_pub_dates(book_attributes['pub_year'])    
    book_attributes.insert(loc=5, column='pub_year_cat', value=pub_year_cat)

    # turn date categories into binary dataframes; merge back into book_attributes
    pub_year_dummies = pd.get_dummies(book_attributes['pub_year_cat'])
    orig_year_dummies = pd.get_dummies(book_attributes['orig_pub_year_cat'])

    book_full_attr = book_attributes.merge(pub_year_dummies,left_index=True, right_index=True)
    book_full_attr = book_full_attr.merge(orig_year_dummies,left_index=True, right_index=True)

    return book_full_attr


def format_book_attributes_for_prediction(book_full_attr):
    """Final formatting step before creating train & predict DFs."""
    
    # move rating column to index 0:
    rating_list = book_full_attr['rating']
    book_full_attr = book_full_attr.drop('rating', 1)
    book_full_attr.insert(loc=0, column='ratings', value=rating_list)

    books_for_prediction = book_full_attr.drop(['subjects', 'status', 'user_id'], 1)

    return books_for_prediction


def rating_categories(rating_list):
    """Normalize ratings: transform 1-5 scale to categorical 1/-1."""

    ratings = []
    for x in rating_list:
        if x > 3:
            ratings.append(1)
        else:
            ratings.append(-1)
    return ratings



def train_model(model, training_set, validation_set):
    """Given an instance of a model, trains that model with validation."""
    model.fit(training_set.iloc[:,8:], training_set.iloc[:, 0])
    return model.predict(validation_set.iloc[:,8:])



def calculate_accuracy(validation_ratings, predicted_ratings):
    """Calculate accuracy of predicted ratings from validation set."""

    correct = 0
    for x, y in zip(validation_ratings, predicted_ratings):
        if x==y:
            correct +=1
    accuracy = correct/float(len(validation_ratings))
    return accuracy


def get_best_predictor(model_1_accuracy, model_2_accuracy, model_1, model_2):
    """Compare accuracy of two models."""

    if model_1_accuracy >= model_2_accuracy:
        return model_1
    else:
        return model_2


def add_recommendations_to_userbooks_table(recs_dataframe, user_id):
    """When book recommendations are generated, add to SQLAlchemy."""

    for i, row in recs_dataframe.iterrows():
        new_userbook = UserBook(user_id=user_id, 
            source = "nextbook-rec",
            status = "rec_no_response",
            book_id= row['book_id'])
        db.session.add(new_userbook)
    db.session.flush()
    
    for i, row in recs_dataframe.iterrows():
        current_userbook = UserBook.query.filter(UserBook.book_id==row['book_id'], 
            UserBook.user_id==user_id).first()
        new_recommendation = Recommendation(date_created=datetime.now(), 
            userbook_id=current_userbook.userbook_id)
        db.session.add(new_recommendation)

    db.session.commit()
    return None


def add_recs_to_recommendations_table(recs_dataframe, user_id):
    """Add recommendations to database. 
    Not standalone; called within create_and_save_recommendations."""

    recs_created = 0
    for i, row in recs_dataframe.iterrows():
        current_userbook = UserBook.query.filter(UserBook.book_id == row['book_id'], 
                            UserBook.user_id == user_id).first()
        new_recommendation = Recommendation(date_created = datetime.now(), 
                                userbook_id = current_userbook.userbook_id)
        db.session.add(new_recommendation)
        recs_created += 1
    db.session.commit()

    return recs_created



def create_and_save_recommendations(model, to_rate, user_id):
    """Using the better model, create recommendations & save to database."""

    model_predictions = model.predict(to_rate.iloc[:, 8:])
    model_recommendations = rating_categories(model_predictions)

    to_rate['recommendations'] = model_recommendations
    to_rate['predicted_ratings'] = model_predictions

    to_recommend = to_rate[to_rate['predicted_ratings']==5]
    add_recommendations_to_userbooks_table(to_recommend, user_id)
    new_recs = add_recs_to_recommendations_table(to_recommend, user_id)

    if len(to_recommend) < 100:
        additional_recommendations = to_rate[to_rate['predicted_ratings']==4]
        add_recommendations_to_userbooks_table(additional_recommendations, user_id)
        next_recs = add_recs_to_recommendations_table(additional_recommendations, user_id)
        new_recs += next_recs

    return new_recs



def send_new_recommendations_alert(new_recs):
    """When recs added to database, alert user & reroute."""

    if new_recs > 0:
        # send email to user saying recommendations are complete
        print "New recs added to DB:", new_recs
    else:
        # email nextbook recommends with error message
        print "no recs created for this user"

def set_first_rec(user_id):
    """Generate a first recommendation for new user."""

    first_rec = Recommendation.query.filter(Recommendation.userbook.has(UserBook.user_id == user_id)).first()
    first_rec.date_provided = date.today()
    db.session.add(first_rec)
    db.session.commit()


### RECOMMENDATIONS SCRIPT: META FUNCTIONS ###

# DATA SETUP
def set_up_data(user_id):

    # import data from psql & unpack into dataframes
    library, book_subjects, subjects = import_data_from_psql(user_id)

    # add book subjects to library & save as new DF
    book_attributes = add_book_subjects_to_library(book_subjects, library)

    # create a list of common subjects; check if each subject in each book's subject list
    common_subjects = get_common_subjects(book_subjects)

    # add each common subject as a binary column in book_attributes
    book_attributes = create_subject_columns(common_subjects, book_attributes)

    # bucket publish dates; turn bucketed date columns into categorical binary columns
    book_full_attr = make_date_columns_categorical_binary(book_attributes)

    # move columns around to format for creating test & train sets
    books_for_prediction = format_book_attributes_for_prediction(book_full_attr)

    # create dfs for fit & prediction
    rated = books_for_prediction[books_for_prediction['ratings'].isin([1,2,3,4,5])]
    to_rate = books_for_prediction[~books_for_prediction['ratings'].isin([1,2,3,4,5])]

    print "created train & predict DFs"

    return [rated, to_rate]


# PREDICTIONS
def generate_new_user_predictions(rated, to_rate, user_id): 
    # calculate sample size; define random train & validate sets
    row_count = len(rated.index)
    if row_count > 1000:
        sample = 1000
    else:
        sample = row_count
    train = int(sample * 0.75)

    rows = random.sample(rated.index, sample)
    rated_train = rated.ix[rows[:train]]
    rated_validate = rated.ix[rows[train:]]

    # create rf & knn models; train models with train & validation sets
    rf = RandomForestClassifier(n_estimators=50)
    rf_predictions = train_model(rf, rated_train, rated_validate)
    print "rf run complete"

    neighbors = KNeighborsClassifier(n_neighbors=11)
    knn_predictions = train_model(neighbors, rated_train, rated_validate)
    print "knn run complete"

    # save validation ratings
    actuals = rated_validate['ratings']

    # Categorize ratings to do/do not recommend
    rf_recommendations = rating_categories(rf_predictions)
    actual_recs = rating_categories(actuals)
    knn_recommendations = rating_categories(knn_predictions)

    # accuracy calculation for algorithm selection
    rf_accuracy = calculate_accuracy(actual_recs, rf_recommendations)
    knn_accuracy = calculate_accuracy(actual_recs, knn_recommendations)
    model = get_best_predictor(rf_accuracy, knn_accuracy, rf, neighbors)

    new_recs = create_and_save_recommendations(model, to_rate, user_id)
    send_new_recommendations_alert(new_recs)
    set_first_rec(user_id)

    return None



# rated, to_rate = set_up_data(user_id)
# generate_new_user_predictions(rated, to_rate)

