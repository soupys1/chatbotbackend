import re
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthAnalyzer:
    def __init__(self):
        self.models_loaded = False
        self.health_keywords = {
            'physical_symptoms': [
                'headache', 'fever', 'cough', 'sore throat', 'nausea', 'vomiting', 'diarrhea',
                'fatigue', 'dizziness', 'chest pain', 'shortness of breath', 'back pain',
                'joint pain', 'muscle pain', 'abdominal pain', 'rash', 'swelling',
                'bleeding', 'bruising', 'numbness', 'tingling', 'weakness', 'pain', 'hurt',
                'ache', 'sick', 'ill', 'tired', 'exhausted', 'dizzy', 'weak'
            ],
            'mental_health': [
                'anxiety', 'depression', 'stress', 'panic', 'worry', 'sadness', 'hopelessness',
                'irritability', 'mood swings', 'insomnia', 'sleep problems', 'concentration',
                'memory', 'suicidal', 'self-harm', 'eating disorder', 'addiction', 'overwhelmed',
                'anxious', 'depressed', 'stressed', 'worried', 'sad', 'angry', 'frustrated'
            ],
            'chronic_conditions': [
                'diabetes', 'hypertension', 'asthma', 'arthritis', 'heart disease',
                'cancer', 'thyroid', 'kidney disease', 'liver disease', 'autoimmune',
                'chronic', 'condition', 'medication', 'treatment', 'diagnosis'
            ],
            'lifestyle': [
                'diet', 'exercise', 'weight', 'smoking', 'alcohol', 'sleep', 'workout',
                'nutrition', 'fitness', 'obesity', 'underweight', 'sedentary', 'food',
                'eating', 'drinking', 'active', 'inactive', 'rest', 'energy'
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
            'can\'t breathe', 'choking', 'overdose', 'poisoning'
        ]
        
        # Try to load models but don't fail if they're not available
        self.load_models()
    
    def load_models(self):
        """Try to load ML models, but continue without them if they fail"""
        try:
            # Try to import and load models
            from transformers import pipeline
            import torch
            
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment",
                device=0 if torch.cuda.is_available() else -1
            )
            
            self.text_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=0 if torch.cuda.is_available() else -1
            )
            
            self.models_loaded = True
            logger.info("AI models loaded successfully")
            
        except Exception as e:
            logger.warning(f"AI models not available: {str(e)}")
            logger.info("Continuing with rule-based analysis")
            self.sentiment_analyzer = None
            self.text_classifier = None
            self.models_loaded = False
    
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
    
    def analyze_sentiment_fallback(self, text: str) -> Dict[str, Any]:
        """Fallback sentiment analysis using keyword-based approach"""
        text = self.preprocess_text(text)
        
        positive_words = ['good', 'better', 'great', 'excellent', 'happy', 'relief', 'improving', 'fine', 'well', 'okay']
        negative_words = ['bad', 'worse', 'terrible', 'awful', 'pain', 'hurt', 'sick', 'ill', 'worry', 'concerned', 'scared']
        
        pos_score = sum(1 for word in positive_words if word in text)
        neg_score = sum(1 for word in negative_words if word in text)
        
        if neg_score > pos_score:
            sentiment = 'negative'
            confidence = min(0.6 + (neg_score - pos_score) * 0.1, 0.9)
        elif pos_score > neg_score:
            sentiment = 'positive' 
            confidence = min(0.6 + (pos_score - neg_score) * 0.1, 0.9)
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'method': 'keyword-based'
        }
    
    def check_emergency(self, text: str) -> Dict[str, Any]:
        """Check if the text indicates an emergency situation"""
        text = self.preprocess_text(text)
        
        emergency_indicators = []
        for keyword in self.emergency_keywords:
            if keyword in text:
                emergency_indicators.append(keyword)
        
        is_emergency = len(emergency_indicators) > 0
        
        return {
            'is_emergency': is_emergency,
            'indicators': emergency_indicators,
            'advice': "⚠️ EMERGENCY: Call emergency services (911) immediately!" if is_emergency else None
        }
    
    def generate_health_advice(self, text: str, categories: Dict[str, float]) -> List[str]:
        """Generate health advice based on detected categories and text"""
        advice = []
        text = self.preprocess_text(text)
        
        # Check for specific symptoms and provide targeted advice
        advice_given = False
        
        for category, score in categories.items():
            if score > 0.2:  # Lower threshold for more responsive advice
                if category in self.health_advice:
                    category_advice = self.health_advice[category]
                    
                    # Find specific symptoms mentioned
                    for symptom, symptom_advice in category_advice.items():
                        if symptom in text:
                            advice.extend(symptom_advice[:2])  # Take first 2 pieces of advice
                            advice_given = True
                            break
                    
                    # If no specific symptom found, provide general category advice
                    if not advice_given:
                        if category == 'physical_symptoms':
                            advice.append("Monitor your symptoms and consider consulting a healthcare provider")
                            advice.append("Rest and stay hydrated while recovering")
                        elif category == 'mental_health':
                            advice.append("Consider speaking with a mental health professional")
                            advice.append("Practice self-care and reach out for support")
                        elif category == 'lifestyle':
                            advice.append("Consider making gradual, sustainable lifestyle changes")
                            advice.append("Focus on one area of improvement at a time")
                        
                        advice_given = True
        
        # Add general health advice if no specific advice was generated
        if not advice_given:
            advice = [
                "Thank you for sharing your health concern with me",
                "Consider consulting a healthcare provider for personalized advice",
                "Maintain healthy lifestyle habits: balanced diet, regular exercise, adequate sleep",
                "Stay hydrated and listen to your body's needs"
            ]
        
        # Remove duplicates and limit to 4 pieces of advice
        unique_advice = []
        seen = set()
        for item in advice:
            if item not in seen:
                unique_advice.append(item)
                seen.add(item)
        
        return unique_advice[:4]
    
    def analyze_health_issue(self, text: str) -> Dict[str, Any]:
        """Main method to analyze health issues and provide advice"""
        
        # Input validation
        if not text or not isinstance(text, str):
            return {
                "error": "Please provide a valid text description of your health concern",
                "original_text": text,
                "processed_text": "",
                "emergency_check": {"is_emergency": False, "indicators": [], "advice": None},
                "health_categories": {"physical_symptoms": 0.0, "mental_health": 0.0, "chronic_conditions": 0.0, "lifestyle": 0.0},
                "sentiment": {"sentiment": "neutral", "confidence": 0.5},
                "urgency_level": "low",
                "health_advice": ["Please describe your health concern so I can provide relevant advice"],
                "recommendation": "Please provide more details about your health concern",
                "models_loaded": self.models_loaded
            }
        
        try:
            # Preprocess text
            processed_text = self.preprocess_text(text)
            
            if not processed_text:
                return {
                    "error": "Please provide a more detailed description",
                    "original_text": text,
                    "processed_text": "",
                    "emergency_check": {"is_emergency": False, "indicators": [], "advice": None},
                    "health_categories": {"physical_symptoms": 0.0, "mental_health": 0.0, "chronic_conditions": 0.0, "lifestyle": 0.0},
                    "sentiment": {"sentiment": "neutral", "confidence": 0.5},
                    "urgency_level": "low",
                    "health_advice": ["Please provide a more detailed description of your health concern"],
                    "recommendation": "Please provide more details",
                    "models_loaded": self.models_loaded
                }
            
            # Check for emergency situations first
            emergency_check = self.check_emergency(processed_text)
            
            # Detect health categories
            health_categories = self.detect_health_categories(processed_text)
            
            # Analyze sentiment
            if self.models_loaded and self.sentiment_analyzer:
                try:
                    sentiment_result = self.sentiment_analyzer(processed_text)[0]
                    # Normalize the output format
                    if 'label' in sentiment_result:
                        sentiment_result['sentiment'] = sentiment_result['label'].lower()
                    if 'score' in sentiment_result:
                        sentiment_result['confidence'] = sentiment_result['score']
                except Exception as e:
                    logger.warning(f"ML sentiment analysis failed: {str(e)}")
                    sentiment_result = self.analyze_sentiment_fallback(processed_text)
            else:
                sentiment_result = self.analyze_sentiment_fallback(processed_text)
            
            # Generate health advice
            health_advice = self.generate_health_advice(processed_text, health_categories)
            
            # Determine urgency level
            urgency_level = "low"
            if emergency_check['is_emergency']:
                urgency_level = "emergency"
            elif health_categories['physical_symptoms'] > 0.4:
                urgency_level = "medium"
            elif health_categories['mental_health'] > 0.4:
                urgency_level = "medium"
            elif sentiment_result.get('sentiment') == 'negative' and sentiment_result.get('confidence', 0) > 0.6:
                urgency_level = "medium"
            
            return {
                "original_text": text,
                "processed_text": processed_text,
                "emergency_check": emergency_check,
                "health_categories": health_categories,
                "sentiment": sentiment_result,
                "urgency_level": urgency_level,
                "health_advice": health_advice,
                "recommendation": self._get_recommendation(urgency_level, health_categories),
                "models_loaded": self.models_loaded,
                "analysis_method": "ML + Rule-based" if self.models_loaded else "Rule-based"
            }
            
        except Exception as e:
            logger.error(f"Health analysis error: {str(e)}")
            return {
                "error": f"Analysis error: {str(e)}",
                "original_text": text,
                "processed_text": text if isinstance(text, str) else "",
                "emergency_check": {"is_emergency": False, "indicators": [], "advice": None},
                "health_categories": {"physical_symptoms": 0.0, "mental_health": 0.0, "chronic_conditions": 0.0, "lifestyle": 0.0},
                "sentiment": {"sentiment": "neutral", "confidence": 0.5},
                "urgency_level": "low",
                "health_advice": [
                    "I apologize, but I encountered an error analyzing your request",
                    "Please try rephrasing your health concern",
                    "For serious health issues, please consult a healthcare provider"
                ],
                "recommendation": "Please try again or consult a healthcare provider",
                "models_loaded": self.models_loaded
            }
    
    def _get_recommendation(self, urgency_level: str, categories: Dict[str, float]) -> str:
        """Get recommendation based on urgency and health categories"""
        if urgency_level == "emergency":
            return "🚨 Seek immediate medical attention or call emergency services"
        elif urgency_level == "medium":
            if categories['mental_health'] > 0.4:
                return "💭 Consider speaking with a mental health professional soon"
            else:
                return "⚕️ Consider consulting a healthcare provider in the near future"
        elif categories['mental_health'] > 0.3:
            return "💭 Consider speaking with a mental health professional"
        elif categories['physical_symptoms'] > 0.3:
            return "⚕️ Monitor symptoms and consult a healthcare provider if they persist or worsen"
        else:
            return "✅ Continue with healthy lifestyle practices and self-care"