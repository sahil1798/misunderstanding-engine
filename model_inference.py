import tensorflow as tf
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
import numpy as np

class ModelInference:
    def __init__(self, model_name):
        print(f"Loading model: {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = TFAutoModelForSequenceClassification.from_pretrained(
            model_name, from_pt=True
        )
        self.labels = ["anger", "joy", "optimism", "sadness"]
        print("Model loaded successfully!")

    def predict_emotion(self, text):
        if not text or not text.strip():
            return {lbl: 0.0 for lbl in self.labels}
        try:
            inputs = self.tokenizer(
                text,
                return_tensors="tf",
                truncation=True,
                padding=True,
                max_length=512,
            )
            outputs = self.model(inputs)
            logits = outputs.logits.numpy()[0]
            probs = tf.nn.softmax(logits).numpy()
            if len(probs) >= len(self.labels):
                probs = probs[:len(self.labels)]
            else:
                probs = np.pad(probs, (0, len(self.labels) - len(probs)))
            return {lbl: float(p) for lbl, p in zip(self.labels, probs)}
        except Exception as e:
            print(f"Prediction error: {e}")
            return {lbl: 0.0 for lbl in self.labels}
