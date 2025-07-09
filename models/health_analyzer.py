import re
import logging
from typing import Dict, List, Any
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Always require ML dependencies for Render deployment
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
import torch

class RoBERTaSentimentAnalyzer:
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.load_model()
    
    def load_model(self):
        MODEL = "cardiffnlp/twitter-roberta-base-sentiment"
        logger.info(f"Loading {MODEL}...")
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL)
        self.model = AutoModelForSequenceClassification.from_pretrained(MODEL)
        logger.info("RoBERTa model loaded successfully")
    
    def preprocess_text(self, text):
        if not isinstance(text, str):
            return ""
        text = text.strip()
        if len(text) > 500:
            text = text[:500]
        return text
    
    def analyze_text(self, text):
        if not text or not isinstance(text, str):
            return {"error": "Invalid text input"}
        if not self.tokenizer or not self.model:
            return {"error": "RoBERTa model not loaded"}
        processed_text = self.preprocess_text(text)
        if not processed_text:
            return {"error": "Empty text after preprocessing"}
        encoded_text = self.tokenizer(
            processed_text, 
            return_tensors='pt', 
            truncation=True, 
            max_length=512,
            padding=True
        )
        with torch.no_grad():
            output = self.model(**encoded_text)
        scores = output.logits[0].detach().numpy()
        scores = softmax(scores)
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
            "processed_text": processed_text,
            "method": "roberta-ml"
        }

class HealthAnalyzer:
    def __init__(self):
        self.roberta_analyzer = RoBERTaSentimentAnalyzer()
        logger.info("ML models initialized successfully (RoBERTa)")
        
        # Enhanced health keywords for better detection
        self.health_keywords = {
            'physical_symptoms': [
                'headache', 'fever', 'cough', 'sore throat', 'nausea', 'vomiting', 'diarrhea',
                'fatigue', 'dizziness', 'chest pain', 'shortness of breath', 'back pain',
                'joint pain', 'muscle pain', 'abdominal pain', 'rash', 'swelling',
                'bleeding', 'bruising', 'numbness', 'tingling', 'weakness', 'pain', 'hurt',
                'ache', 'sick', 'ill', 'tired', 'exhausted', 'dizzy', 'weak', 'sore',
                'stiff', 'cramp', 'spasm', 'throbbing', 'sharp pain', 'dull pain'
            ],
            'mental_health': [
                'anxiety', 'depression', 'stress', 'panic', 'worry', 'sadness', 'hopelessness',
                'irritability', 'mood swings', 'insomnia', 'sleep problems', 'concentration',
                'memory', 'suicidal', 'self-harm', 'eating disorder', 'addiction', 'overwhelmed',
                'anxious', 'depressed', 'stressed', 'worried', 'sad', 'angry', 'frustrated',
                'lonely', 'isolated', 'worthless', 'guilty', 'shame', 'fear', 'scared',
                'nervous', 'tense', 'restless', 'agitated', 'moody', 'emotional'
            ],
            'chronic_conditions': [
                'diabetes', 'hypertension', 'asthma', 'arthritis', 'heart disease',
                'cancer', 'thyroid', 'kidney disease', 'liver disease', 'autoimmune',
                'chronic', 'condition', 'medication', 'treatment', 'diagnosis',
                'high blood pressure', 'low blood pressure', 'heart condition',
                'lung condition', 'digestive issue', 'stomach problem'
            ],
            'lifestyle': [
                'diet', 'exercise', 'weight', 'smoking', 'alcohol', 'sleep', 'workout',
                'nutrition', 'fitness', 'obesity', 'underweight', 'sedentary', 'food',
                'eating', 'drinking', 'active', 'inactive', 'rest', 'energy',
                'lifestyle', 'habits', 'routine', 'physical activity', 'sports'
            ]
        }
        
        # Enhanced health advice with more specific responses
        self.health_advice = {
            'physical_symptoms': {
                'headache': [
                    "Try resting in a quiet, dark room to reduce stimulation",
                    "Stay well-hydrated with water throughout the day",
                    "Consider over-the-counter pain relief if appropriate",
                    "Apply a cold or warm compress to your head or neck",
                    "If headaches persist or worsen, consult a healthcare provider"
                ],
                'fever': [
                    "Rest and drink plenty of fluids to stay hydrated",
                    "Monitor your temperature regularly",
                    "Consider fever-reducing medication if recommended by a healthcare provider",
                    "Keep cool with light clothing and room temperature",
                    "Seek medical attention if fever is very high or persists"
                ],
                'cough': [
                    "Stay hydrated to help thin mucus secretions",
                    "Use honey (for adults) to soothe throat irritation",
                    "Consider a humidifier to add moisture to the air",
                    "Avoid irritants like smoke and strong scents",
                    "See a healthcare provider if cough persists or worsens"
                ],
                'fatigue': [
                    "Ensure you're getting adequate sleep (7-9 hours nightly)",
                    "Maintain regular sleep and wake times",
                    "Eat nutritious, balanced meals regularly",
                    "Stay hydrated throughout the day",
                    "Consider if stress or other factors might be contributing"
                ],
                'pain': [
                    "Rest the affected area if possible",
                    "Apply ice for acute injuries or heat for muscle tension",
                    "Consider gentle stretching or movement as tolerated",
                    "Monitor pain levels and patterns",
                    "Consult a healthcare provider for persistent or severe pain"
                ]
            },
            'mental_health': {
                'anxiety': [
                    "Practice deep breathing exercises (4-7-8 technique)",
                    "Try progressive muscle relaxation",
                    "Limit caffeine intake, especially if sensitive",
                    "Maintain regular sleep schedules",
                    "Consider speaking with a mental health professional"
                ],
                'depression': [
                    "Try to maintain daily routines, even simple ones",
                    "Stay connected with supportive friends and family",
                    "Engage in gentle physical activity like walking",
                    "Spend time outdoors in natural light when possible",
                    "Remember that depression is treatable - consider professional help"
                ],
                'stress': [
                    "Practice mindfulness or meditation techniques",
                    "Take regular breaks during demanding activities",
                    "Engage in physical activity to release tension",
                    "Set realistic boundaries and prioritize self-care",
                    "Consider stress management counseling if needed"
                ]
            },
            'lifestyle': {
                'diet': [
                    "Focus on whole foods: fruits, vegetables, lean proteins, whole grains",
                    "Limit processed foods, added sugars, and excessive fats",
                    "Stay hydrated with water as your primary beverage",
                    "Eat regular, balanced meals and avoid skipping meals",
                    "Consider consulting a registered dietitian for personalized guidance"
                ],
                'exercise': [
                    "Start with activities you enjoy to build consistency",
                    "Aim for at least 150 minutes of moderate activity weekly",
                    "Include both cardiovascular and strength training exercises",
                    "Begin gradually and progressively increase intensity",
                    "Always warm up before and cool down after exercise"
                ],
                'sleep': [
                    "Maintain consistent sleep and wake times",
                    "Create a relaxing bedtime routine",
                    "Keep your bedroom cool, dark, and quiet",
                    "Avoid screens and stimulating activities before bed",
                    "Limit caffeine and large meals close to bedtime"
                ]
            }
        }
        
        self.emergency_keywords = [
            'chest pain', 'heart attack', 'stroke', 'severe bleeding', 'unconscious',
            'difficulty breathing', 'severe head injury', 'suicidal thoughts', 'suicide',
            'severe allergic reaction', 'broken bone', 'severe burn', 'emergency',
            'can\'t breathe', 'choking', 'overdose', 'poisoning', 'cardiac arrest',
            'severe trauma', 'life threatening', 'critical condition'
        ]
        
        logger.info("Health analyzer initialized - ML available: True")
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text"""
        if not isinstance(text, str):
            return ""
        
        # Basic cleaning
        text = text.strip().lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def detect_health_categories(self, text: str) -> Dict[str, float]:
        """Detect health-related categories in the text"""
        text = self.preprocess_text(text)
        categories = {
            'physical_symptoms': 0.0,
            'mental_health': 0.0,
            'chronic_conditions': 0.0,
            'lifestyle': 0.0
        }
        
        # Enhanced keyword-based detection
        for category, keywords in self.health_keywords.items():
            matches = 0
            total_keywords = len(keywords)
            
            for keyword in keywords:
                if keyword in text:
                    matches += 1
                    # Give extra weight to exact matches
                    if f" {keyword} " in f" {text} ":
                        matches += 0.5
            
            # Calculate score with better weighting
            if matches > 0:
                categories[category] = min(matches / (total_keywords * 0.3), 1.0)
        
        return categories
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        return self.roberta_analyzer.analyze_text(text)
    
    def check_emergency(self, text: str) -> Dict[str, Any]:
        """Check if the text indicates an emergency situation"""
        text = self.preprocess_text(text)
        
        emergency_detected = False
        emergency_keywords_found = []
        
        for keyword in self.emergency_keywords:
            if keyword in text:
                emergency_detected = True
                emergency_keywords_found.append(keyword)
        
        return {
            "is_emergency": emergency_detected,
            "emergency_keywords": emergency_keywords_found,
            "recommendation": "Call emergency services immediately" if emergency_detected else None
        }
    
    def generate_health_advice(self, text: str, categories: Dict[str, float]) -> List[str]:
        """Generate health advice based on detected categories"""
        text = self.preprocess_text(text)
        advice = []
        
        # Find the most relevant category
        max_category = max(categories.items(), key=lambda x: x[1])
        
        if max_category[1] > 0.3:  # Only provide advice if category is detected
            category_name = max_category[0]
            
            # Look for specific symptoms in the text
            for symptom, symptom_advice in self.health_advice.get(category_name, {}).items():
                if symptom in text:
                    advice.extend(symptom_advice[:3])  # Take first 3 pieces of advice
                    break
            
            # If no specific symptom advice, provide general category advice
            if not advice and category_name in self.health_advice:
                general_advice = self.health_advice[category_name]
                if general_advice:
                    # Take advice from the first available subcategory
                    first_subcategory = list(general_advice.values())[0]
                    advice.extend(first_subcategory[:3])
        
        # Add general health advice if no specific advice was generated
        if not advice:
            advice = [
                "Consider consulting with a healthcare provider for personalized advice",
                "Maintain a healthy lifestyle with regular exercise and balanced nutrition",
                "Keep track of your symptoms and any changes over time"
            ]
        
        return advice[:5]  # Limit to 5 pieces of advice
    
    def analyze_health_issue(self, text: str) -> Dict[str, Any]:
        """Main method to analyze health issues and provide comprehensive response"""
        try:
            if not text or not isinstance(text, str):
                return {
                    "error": "Invalid input: text must be a non-empty string",
                    "success": False
                }
            
            # Preprocess text
            processed_text = self.preprocess_text(text)
            
            if not processed_text:
                return {
                    "error": "Text is empty after preprocessing",
                    "success": False
                }
            
            # Analyze different aspects
            categories = self.detect_health_categories(processed_text)
            sentiment = self.analyze_sentiment(processed_text)
            emergency_check = self.check_emergency(processed_text)
            
            # Determine urgency level
            urgency_level = self._get_urgency_level(emergency_check, categories, sentiment)
            
            # Generate advice
            advice = self.generate_health_advice(processed_text, categories)
            
            # Get recommendation
            recommendation = self._get_recommendation(urgency_level, categories)
            
            return {
                "success": True,
                "text": text,
                "health_categories": categories,
                "sentiment_analysis": sentiment,
                "emergency_detection": emergency_check,
                "urgency_level": urgency_level,
                "advice": advice,
                "recommendation": recommendation,
                "analysis_method": "ml-roberta",
                "ml_available": True
            }
            
        except Exception as e:
            logger.error(f"Error in health analysis: {str(e)}")
            return {
                "error": f"Analysis failed: {str(e)}",
                "success": False
            }
    
    def _get_urgency_level(self, emergency_check: Dict, categories: Dict, sentiment: Dict) -> str:
        """Determine urgency level based on analysis results"""
        if emergency_check.get("is_emergency", False):
            return "emergency"
        
        # Check for high negative sentiment
        if sentiment.get("sentiment") == "negative" and sentiment.get("confidence", 0) > 0.7:
            return "medium"
        
        # Check for high category scores
        max_category_score = max(categories.values())
        if max_category_score > 0.7:
            return "medium"
        
        return "low"
    
    def _get_recommendation(self, urgency_level: str, categories: Dict[str, float]) -> str:
        """Get recommendation based on urgency level and categories"""
        if urgency_level == "emergency":
            return "Seek immediate medical attention or call emergency services."
        elif urgency_level == "medium":
            return "Consider consulting a healthcare provider for evaluation."
        else:
            return "Monitor symptoms and consider lifestyle modifications."
    
    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple texts in batch"""
        results = []
        
        for text in texts:
            try:
                result = self.analyze_health_issue(text)
                results.append(result)
            except Exception as e:
                logger.error(f"Error analyzing text '{text[:50]}...': {str(e)}")
                results.append({
                    "error": f"Analysis failed: {str(e)}",
                    "success": False,
                    "text": text
                })
        
        return results