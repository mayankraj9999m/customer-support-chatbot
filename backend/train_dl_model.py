import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, TextVectorization, Embedding, GlobalAveragePooling1D
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pickle
import os

# Set paths relative to the current directory
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Final_merged_reduced_intents_cleaned_153k_v15.csv')
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'tf_intent_model.keras')
ENCODER_PATH = os.path.join(os.path.dirname(__file__), 'tf_label_encoder.pkl')

def train_dl_model():
    print(f"Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=['instructions', 'intents'])
    print(f"Dataset shape: {df.shape}")
    
    # Strip emojis and non-ascii characters to avoid UnicodeEncodeError when saving the model on Windows
    df['instructions'] = df['instructions'].astype(str).str.encode('ascii', 'ignore').str.decode('ascii')
    
    X = df['instructions'].values
    y = df['intents'].values
    
    # Encode labels
    print("Encoding labels...")
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    num_classes = len(label_encoder.classes_)
    
    with open(ENCODER_PATH, 'wb') as f:
        pickle.dump(label_encoder, f)
        
    print("Splitting dataset...")
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
    
    # Text Vectorization
    print("Configuring TextVectorization...")
    vocab_size = 10000
    sequence_length = 50
    
    vectorize_layer = TextVectorization(
        max_tokens=vocab_size,
        output_mode='int',
        output_sequence_length=sequence_length
    )
    vectorize_layer.adapt(X_train)
    
    # Build Keras Model
    print("Building TensorFlow model...")
    model = Sequential([
        vectorize_layer,
        Embedding(vocab_size, 64, mask_zero=True),
        GlobalAveragePooling1D(),
        Dense(64, activation='relu'),
        Dropout(0.5),
        Dense(num_classes, activation='softmax')
    ])
    
    model.compile(loss='sparse_categorical_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])
                  
    print("Training model...")
    model.fit(X_train, y_train, epochs=5, batch_size=64, validation_data=(X_test, y_test))
    
    print(f"Evaluating model...")
    loss, accuracy = model.evaluate(X_test, y_test)
    print(f"Test Accuracy: {accuracy:.4f}")
    
    print(f"Saving model to {MODEL_PATH}...")
    model.save(MODEL_PATH)
    print("Training complete!")

if __name__ == '__main__':
    train_dl_model()
