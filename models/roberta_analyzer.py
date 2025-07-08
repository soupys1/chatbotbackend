from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
import logging
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RoBERTaSentimentAnalyzer:
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load RoBERTa model for sentiment analysis"""
        try:
            MODEL = "cardiffnlp/twitter-roberta-base-sentiment"
            logger.info(f"Loading {MODEL}...")
            
            self.tokenizer = AutoTokenizer.from_pretrained(MODEL)
            self.model = AutoModelForSequenceClassification.from_pretrained(MODEL)
            
            logger.info("RoBERTa model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading RoBERTa model: {str(e)}")
            raise
    
    def preprocess_text(self, text):
        """Clean and preprocess text"""
        if not isinstance(text, str):
            return ""
        
        # Basic cleaning
        text = text.strip()
        
        # Truncate if too long (RoBERTa has 512 token limit)
        if len(text) > 500:  # Conservative limit to account for tokenization
            text = text[:500]
        
        return text
    
    def analyze_text(self, text):
        """Analyze sentiment using RoBERTa model"""
        if not text or not isinstance(text, str):
            return {"error": "Invalid text input"}
        
        if not self.tokenizer or not self.model:
            return {"error": "RoBERTa model not loaded"}
        
        try:
            # Preprocess text
            processed_text = self.preprocess_text(text)
            
            if not processed_text:
                return {"error": "Empty text after preprocessing"}
            
            # Tokenize
            encoded_text = self.tokenizer(
                processed_text, 
                return_tensors='pt', 
                truncation=True, 
                max_length=512,
                padding=True
            )
            
            # Get model output
            with torch.no_grad():
                output = self.model(**encoded_text)
            
            # Convert to probabilities
            scores = output.logits[0].detach().numpy()
            scores = softmax(scores)
            
            # Map to sentiment labels
            sentiment_labels = ['negative', 'neutral', 'positive']
            predicted_label = sentiment_labels[scores.argmax()]
            confidence = float(scores.max())
            
            return {
                "sentiment": predicted_label,
                "confidence": confidence,
                "scores": {
                    "negative": float(scores[0]),
                    "neutral": float(scores[1]),
                    "positive": float(scores[2])
                },
                "original_text": text,
                "processed_text": processed_text
            }
            
        except Exception as e:
            logger.error(f"RoBERTa analysis error: {str(e)}")
            return {
                "error": str(e),
                "sentiment": "neutral",
                "confidence": 0.0,
                "original_text": text
            }
    
    def analyze_batch(self, texts):
        """Analyze multiple texts"""
        if not isinstance(texts, list):
            return {"error": "Input must be a list of texts"}
        
        results = []
        for i, text in enumerate(texts):
            try:
                result = self.analyze_text(text)
                result['index'] = i
                results.append(result)
            except Exception as e:
                logger.error(f"Error analyzing text {i}: {str(e)}")
                results.append({
                    'index': i,
                    'error': str(e),
                    'original_text': text,
                    'sentiment': 'neutral',
                    'confidence': 0.0
                })
        
        return results