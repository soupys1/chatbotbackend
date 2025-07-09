# Backend - Flask Server (app.py)
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
import logging
from datetime import datetime

app = Flask(__name__)

# Render-specific CORS configuration
CORS(app, origins=["https://your-frontend-domain.onrender.com", "http://localhost:3000"])



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global sentiment analyzer
sentiment_analyzer = None

def initialize_sentiment_analyzer():
    """Initialize the RoBERTa sentiment analyzer"""
    global sentiment_analyzer
    try:
        logger.info("Initializing RoBERTa sentiment analyzer...")
        sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            return_all_scores=True
        )
        logger.info("RoBERTa sentiment analyzer initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing sentiment analyzer: {e}")
        raise

def analyze_sentiment(text):
    """Analyze sentiment of given text"""
    if not sentiment_analyzer:
        return {"label": "UNKNOWN", "score": 0.0}
    
    try:
        results = sentiment_analyzer(text)
        # Get the highest scoring sentiment
        best_result = max(results[0], key=lambda x: x['score'])
        return {
            "label": best_result['label'],
            "score": best_result['score'],
            "all_scores": results[0]
        }
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        return {"label": "ERROR", "score": 0.0}

def generate_response(message, sentiment):
    """Generate chatbot response based on sentiment"""
    label = sentiment.get("label", "UNKNOWN").upper()
    score = sentiment.get("score", 0.0)
    
    responses = {
        "LABEL_2": [  # Positive
            "That's wonderful to hear! I'm glad you're feeling positive! 😊",
            "Your positive energy is contagious! Tell me more!",
            "I love your enthusiasm! How can I help you today?",
            "That sounds great! I'm here to chat about anything you'd like!"
        ],
        "LABEL_0": [  # Negative
            "I'm sorry you're feeling down. I'm here to listen and help if I can. 💙",
            "That sounds challenging. Would you like to talk about it?",
            "I understand this might be difficult. How can I support you?",
            "I'm here for you. Sometimes it helps to share what's on your mind."
        ],
        "LABEL_1": [  # Neutral
            "I see. Tell me more about that.",
            "That's interesting. What are your thoughts on it?",
            "I'm listening. Please continue.",
            "Thanks for sharing. What would you like to discuss?"
        ]
    }
    
    import random
    response_list = responses.get(label, responses["LABEL_1"])
    base_response = random.choice(response_list)
    
    # Add confidence info for transparency
    confidence = f" (Sentiment: {label.replace('LABEL_', {0: 'Negative', 1: 'Neutral', 2: 'Positive'}.get(int(label.split('_')[1]), 'Unknown'))}, Confidence: {score:.2f})"
    
    return base_response + confidence

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": sentiment_analyzer is not None
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
        
        message = data['message'].strip()
        
        if not message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        logger.info(f"Processing message: {message}")
        
        # Analyze sentiment
        sentiment = analyze_sentiment(message)
        
        # Generate response
        response = generate_response(message, sentiment)
        
        return jsonify({
            "response": response,
            "sentiment": sentiment,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/sentiment', methods=['POST'])
def sentiment_only():
    """Endpoint for sentiment analysis only"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({"error": "Text is required"}), 400
        
        text = data['text'].strip()
        
        if not text:
            return jsonify({"error": "Text cannot be empty"}), 400
        
        sentiment = analyze_sentiment(text)
        
        return jsonify({
            "sentiment": sentiment,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error processing sentiment request: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Initialize the sentiment analyzer
    initialize_sentiment_analyzer()
    
    # Render uses PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)