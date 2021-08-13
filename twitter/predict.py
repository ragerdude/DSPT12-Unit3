import pandas as pd
from .orm_model import Tweet, Author
from sklearn.linear_model import LogisticRegression

def get_most_likely_author(tweet_body, spacy_model):
    authors = Author.query.all()
    features = pd.DataFrame()
    target = pd.Series()
    ###Example One
    for a in authors:
        for t in a.tweets:
            if not len(features) > 0:
                features = pd.DataFrame(t.vect).T
            else:
                features = pd.concat([pd.DataFrame(t.vect).T, features])
            target = target.append(pd.Series([a.name]))
    target.reset_index(inplace=True, drop=True)
    features.reset_index(inplace=True, drop=True)
    model = LogisticRegression()
    model.fit(X=features, y=target)
    likely_author = model.predict([spacy_model(tweet_body).vector])
    return likely_author