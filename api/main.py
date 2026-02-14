from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pickle
import re
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# ----------------------------
# Model Metadata
# ----------------------------
MODEL_NAME = "Email Phishing Detector"
MODEL_VERSION = "1.0.0"
MODEL_TYPE = "TF-IDF + Logistic Regression"


# ----------------------------
# Load saved model & vectorizer
# ----------------------------
with open("models/email_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("models/tfidf_vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)


# ----------------------------
# Text cleaning function
# ----------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


@app.get("/")
def home():
    return {"message": "Phishing Detection API is running"}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "model_version": MODEL_VERSION
    }



from pydantic import BaseModel, Field

# ----------------------------
# Request schema
# ----------------------------
class EmailRequest(BaseModel):
    text: str = Field(..., min_length=5, description="Email content to analyze")


# ----------------------------
# Prediction endpoint
# ----------------------------
import time
from fastapi import HTTPException

@app.post("/predict")
def predict_email(data: EmailRequest):
    start_time = time.time()

    try:
        # Clean input
        cleaned = clean_text(data.text)

        # Convert to vector
        vector = vectorizer.transform([cleaned])

        # Predict class
        prediction = model.predict(vector)[0]

        # Predict probability
        probabilities = model.predict_proba(vector)[0]
        confidence = max(probabilities)

        is_phishing = bool(prediction)
        result = "Phishing Email" if is_phishing else "Safe Email"

        processing_time = round(time.time() - start_time, 4)

        logging.info(
            f"Input: {cleaned[:50]}... | "
            f"Prediction: {prediction} | "
            f"Confidence: {round(float(confidence),4)} | "
            f"Time: {processing_time}s"
        )

        return {
            "model_name": MODEL_NAME,
            "model_version": MODEL_VERSION,
            "model_type": MODEL_TYPE,
            "prediction": result,
            "is_phishing": is_phishing,
            "confidence_score": round(float(confidence), 4),
            "processing_time_seconds": processing_time
        }


    except Exception as e:
        logging.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")




