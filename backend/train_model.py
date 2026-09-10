import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pickle
import os

# Set paths relative to the current directory
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Final_merged_reduced_intents_cleaned_153k_v15.csv')
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'intent_model.pkl')

def train_model():
    print(f"Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    # Drop any nulls
    df = df.dropna(subset=['instructions', 'intents'])
    
    print(f"Dataset shape: {df.shape}")
    
    X = df['instructions']
    y = df['intents']
    
    # Split the data (80% train, 20% test)
    print("Splitting dataset into train and test sets...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create a pipeline
    print("Training TF-IDF + Logistic Regression model...")
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=10000, stop_words='english')),
        ('clf', LogisticRegression(max_iter=1000, n_jobs=-1)) # n_jobs=-1 to use all cores
    ])
    
    pipeline.fit(X_train, y_train)
    
    print("Evaluating model...")
    y_pred = pipeline.predict(X_test)
    print(classification_report(y_test, y_pred))
    
    print(f"Saving model to {MODEL_PATH}...")
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(pipeline, f)
        
    print("Training complete!")

if __name__ == '__main__':
    train_model()
