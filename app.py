from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import io
import logging
import os

# Import your health analyzer
from models.health_analyzer import HealthAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize health analyzer (this will take some time on first run)
print("Loading health analysis models...")
health_analyzer = HealthAnalyzer()
print("Health analysis models loaded successfully!")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "message": "Health Analysis API is running",
        "models": ["sentiment-analysis", "health-classification", "advice-generation"]
    })

@app.route('/analyze-health', methods=['POST'])
def analyze_health():
    """Analyze health issues and provide advice"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' field in request"}), 400
        
        text = data['text']
        if not text or len(text.strip()) == 0:
            return jsonify({"error": "Text cannot be empty"}), 400
        
        # Perform health analysis
        result = health_analyzer.analyze_health_issue(text)
        
        return jsonify({
            "success": True,
            "data": result
        })
    
    except Exception as e:
        logger.error(f"Error in /analyze-health endpoint: {str(e)}")
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/analyze-health-batch', methods=['POST'])
def analyze_health_batch():
    """Analyze health issues for multiple texts"""
    try:
        data = request.get_json()
        
        if not data or 'texts' not in data:
            return jsonify({"error": "Missing 'texts' field in request"}), 400
        
        texts = data['texts']
        
        if not isinstance(texts, list):
            return jsonify({"error": "'texts' must be a list"}), 400
        
        if len(texts) > 20:  # Limit batch size for performance
            return jsonify({"error": "Maximum 20 texts allowed per batch"}), 400
        
        # Filter out empty texts
        texts = [text for text in texts if text and text.strip()]
        
        if len(texts) == 0:
            return jsonify({"error": "No valid texts provided"}), 400
        
        # Perform batch health analysis
        results = health_analyzer.analyze_batch(texts)
        
        # Calculate summary statistics
        urgency_counts = {"emergency": 0, "medium": 0, "low": 0}
        category_counts = {"physical_symptoms": 0, "mental_health": 0, "chronic_conditions": 0, "lifestyle": 0}
        valid_results = [r for r in results if 'error' not in r]
        
        for result in valid_results:
            if 'urgency_level' in result:
                urgency_counts[result['urgency_level']] += 1
            
            if 'health_categories' in result and isinstance(result['health_categories'], dict):
                for category, score in result['health_categories'].items():
                    if isinstance(score, (int, float)) and score > 0.3:  # Threshold for counting
                        category_counts[category] += 1
        
        summary = {
            "total": len(results),
            "valid": len(valid_results),
            "errors": len(results) - len(valid_results),
            "urgency_distribution": urgency_counts,
            "category_distribution": category_counts
        }
        
        return jsonify({
            "success": True,
            "data": results,
            "summary": summary
        })
    
    except Exception as e:
        logger.error(f"Error in /analyze-health-batch endpoint: {str(e)}")
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/analyze-health-file', methods=['POST'])
def analyze_health_file():
    """Analyze health issues from uploaded CSV file"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not file.filename or not file.filename.endswith('.csv'):
            return jsonify({"error": "Only CSV files are supported"}), 400
        
        # Read CSV file
        csv_data = file.read()
        csv_stream = io.StringIO(csv_data.decode('utf-8'))
        csv_reader = csv.DictReader(csv_stream)
        
        # Get all rows first to count them
        rows = list(csv_reader)
        original_rows = len(rows)
        
        # Find text column
        text_column = None
        possible_columns = ['text', 'Text', 'symptoms', 'Symptoms', 'issue', 'Issue', 'concern', 'Concern', 'description', 'Description']
        
        if rows:
            for col in possible_columns:
                if col in rows[0]:
                    text_column = col
                    break
        
        if text_column is None:
            return jsonify({
                "error": f"No text column found. Available columns: {list(rows[0].keys()) if rows else []}"
            }), 400
        
        # Limit number of rows for performance
        if len(rows) > 50:
            rows = rows[:50]
            logger.info(f"Limited analysis to first 50 rows (original: {original_rows})")
        
        # Convert to string and filter valid texts
        texts = [str(row[text_column]) for row in rows if row[text_column] and row[text_column].strip() and row[text_column] != 'nan']
        
        if len(texts) == 0:
            return jsonify({"error": "No valid texts found in the file"}), 400
        
        # Perform batch health analysis
        results = health_analyzer.analyze_batch(texts)
        
        # Calculate summary statistics
        urgency_counts = {"emergency": 0, "medium": 0, "low": 0}
        category_counts = {"physical_symptoms": 0, "mental_health": 0, "chronic_conditions": 0, "lifestyle": 0}
        valid_results = [r for r in results if 'error' not in r]
        
        for result in valid_results:
            if 'urgency_level' in result:
                urgency_counts[result['urgency_level']] += 1
            
            if 'health_categories' in result and isinstance(result['health_categories'], dict):
                for category, score in result['health_categories'].items():
                    if isinstance(score, (int, float)) and score > 0.3:
                        category_counts[category] += 1
        
        summary = {
            "total": len(results),
            "processed_rows": len(texts),
            "original_file_rows": original_rows,
            "valid": len(valid_results),
            "errors": len(results) - len(valid_results),
            "urgency_distribution": urgency_counts,
            "category_distribution": category_counts
        }
        
        return jsonify({
            "success": True,
            "summary": summary,
            "sample_results": results[:5],  # Return first 5 results as sample
            "column_used": text_column
        })
    
    except Exception as e:
        logger.error(f"Error in /analyze-health-file endpoint: {str(e)}")
        return jsonify({"error": str(e), "success": False}), 500

# Keep the old sentiment analysis endpoints for backward compatibility
@app.route('/analyze', methods=['POST'])
def analyze_single():
    """Analyze sentiment for single text (legacy endpoint)"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' field in request"}), 400
        
        text = data['text']
        if not text or len(text.strip()) == 0:
            return jsonify({"error": "Text cannot be empty"}), 400
        
        # Perform health analysis instead of just sentiment
        result = health_analyzer.analyze_health_issue(text)
        
        return jsonify({
            "success": True,
            "data": result
        })
    
    except Exception as e:
        logger.error(f"Error in /analyze endpoint: {str(e)}")
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/analyze-batch', methods=['POST'])
def analyze_batch():
    """Analyze sentiment for multiple texts (legacy endpoint)"""
    try:
        data = request.get_json()
        
        if not data or 'texts' not in data:
            return jsonify({"error": "Missing 'texts' field in request"}), 400
        
        texts = data['texts']
        
        if not isinstance(texts, list):
            return jsonify({"error": "'texts' must be a list"}), 400
        
        if len(texts) > 50:  # Limit batch size for performance
            return jsonify({"error": "Maximum 50 texts allowed per batch"}), 400
        
        # Filter out empty texts
        texts = [text for text in texts if text and text.strip()]
        
        if len(texts) == 0:
            return jsonify({"error": "No valid texts provided"}), 400
        
        # Perform batch health analysis
        results = health_analyzer.analyze_batch(texts)
        
        # Calculate summary statistics
        urgency_counts = {"emergency": 0, "medium": 0, "low": 0}
        valid_results = [r for r in results if 'error' not in r]
        
        for result in valid_results:
            if 'urgency_level' in result:
                urgency_counts[result['urgency_level']] += 1
        
        summary = {
            "total": len(results),
            "valid": len(valid_results),
            "errors": len(results) - len(valid_results),
            "urgency_distribution": urgency_counts
        }
        
        return jsonify({
            "success": True,
            "data": results,
            "summary": summary
        })
    
    except Exception as e:
        logger.error(f"Error in /analyze-batch endpoint: {str(e)}")
        return jsonify({"error": str(e), "success": False}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)
