import os
import pickle
import spacy
import tensorflow as tf
import re

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tf_intent_model.keras')
ENCODER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tf_label_encoder.pkl')

class MLService:
    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.nlp = None

    def load_models(self):
        # Load SpaCy for NER
        try:
            print("Loading spaCy model...")
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("spaCy en_core_web_sm not found. Please run: python -m spacy download en_core_web_sm")
        
        # Load TensorFlow model
        if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
            print(f"Loading TensorFlow model from {MODEL_PATH}...")
            self.model = tf.keras.models.load_model(MODEL_PATH)
            with open(ENCODER_PATH, 'rb') as f:
                self.label_encoder = pickle.load(f)

    def predict_intent(self, user_msg: str):
        if not self.model or not self.label_encoder:
            raise RuntimeError("ML Models not loaded")
        
        import numpy as np
        predictions = self.model.predict(tf.constant([user_msg]))
        predicted_class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_idx])
        predicted_intent = self.label_encoder.inverse_transform([predicted_class_idx])[0]
        return predicted_intent, confidence

    def extract_entities_advanced(self, text: str) -> dict:
        entities = {}
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                label = ent.label_.lower()
                if label not in entities:
                    entities[label] = []
                entities[label].append(ent.text)
                
        order_match = re.search(r'(?:#|order\s+)(\d+)', text, re.IGNORECASE)
        if order_match:
            entities['order_id'] = [order_match.group(1)]
            
        return entities

ml_service = MLService()
