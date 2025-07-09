# ML-Enhanced Health Chatbot Deployment Guide

## Overview

This health chatbot now supports both rule-based analysis and ML-enhanced analysis using RoBERTa models. The system automatically detects available dependencies and falls back gracefully.

## Deployment Options

### 1. Vercel Deployment (Recommended for Production)
- **File**: `requirements.txt` (minimal dependencies)
- **Analysis**: Rule-based only
- **Pros**: Fast deployment, reliable, no build issues
- **Cons**: No ML capabilities

### 2. Local Development with ML
- **File**: `requirements-ml.txt` (full ML dependencies)
- **Analysis**: ML-enhanced with RoBERTa sentiment analysis
- **Pros**: Full ML capabilities, better sentiment analysis
- **Cons**: Requires more resources, longer startup time

### 3. Other Platforms (Render, Railway, etc.)
- **File**: `requirements-ml.txt` (if platform supports ML)
- **Analysis**: ML-enhanced
- **Pros**: Full capabilities
- **Cons**: May have build issues with large dependencies

## How the Hybrid System Works

### Automatic Detection
The system automatically detects if ML dependencies are available:

```python
# In health_analyzer.py
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    from scipy.special import softmax
    import torch
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
```

### Fallback Mechanism
- If ML models are available: Uses RoBERTa for sentiment analysis
- If ML models are not available: Falls back to rule-based sentiment analysis
- Health category detection is always rule-based (more reliable for health domains)

### Response Indicators
The API response includes indicators of which method was used:

```json
{
  "analysis_method": "ml-enhanced",  // or "rule-based"
  "ml_available": true,              // or false
  "sentiment_analysis": {
    "method": "roberta-ml"           // or "rule-based"
  }
}
```

## Setup Instructions

### For Vercel Deployment (Production)
1. Use `requirements.txt` (already configured)
2. Deploy to Vercel with root directory set to `backend/`
3. System will use rule-based analysis automatically

### For Local Development with ML
1. Install ML dependencies:
   ```bash
   pip install -r requirements-ml.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. System will automatically use ML models if available

### For Other Platforms
1. Check if the platform supports ML dependencies
2. If yes: Use `requirements-ml.txt`
3. If no: Use `requirements.txt`

## API Endpoints

All endpoints work the same way regardless of ML availability:

- `POST /analyze-health` - Single text analysis
- `POST /analyze-health-batch` - Batch analysis
- `POST /analyze-health-file` - CSV file analysis
- `GET /health` - Health check

## Performance Considerations

### Rule-based Analysis (Vercel)
- **Startup time**: ~1-2 seconds
- **Memory usage**: ~50-100MB
- **Response time**: ~100-200ms
- **Accuracy**: Good for health categories, basic sentiment

### ML-enhanced Analysis (Local/Other platforms)
- **Startup time**: ~10-30 seconds (model loading)
- **Memory usage**: ~1-2GB
- **Response time**: ~200-500ms
- **Accuracy**: Excellent sentiment analysis, same health categories

## Troubleshooting

### ML Models Not Loading
If you see warnings about ML models not loading:
1. Check if all dependencies are installed: `pip install -r requirements-ml.txt`
2. Check internet connection (models are downloaded from Hugging Face)
3. Check available memory (models require ~1GB RAM)

### Fallback to Rule-based
If ML models fail to load, the system automatically falls back to rule-based analysis. This is normal and expected behavior.

### Vercel Build Issues
If you encounter build issues on Vercel:
1. Ensure you're using `requirements.txt` (not `requirements-ml.txt`)
2. Check that `venv/` is not tracked in git
3. Verify `vercel.json` is in the `backend/` directory

## Testing

### Test ML vs Rule-based
You can test both approaches by:

1. **With ML** (local development):
   ```bash
   pip install -r requirements-ml.txt
   python app.py
   ```

2. **Without ML** (production-like):
   ```bash
   pip install -r requirements.txt
   python app.py
   ```

### API Response Comparison
Compare the `analysis_method` and `ml_available` fields in responses to verify which method is being used.

## Future Enhancements

1. **Model Caching**: Cache downloaded models for faster startup
2. **Health-specific ML**: Train custom models for health domain
3. **Multiple Models**: Support for different ML models
4. **Model Quantization**: Reduce model size for deployment

## Support

- For deployment issues: Check platform-specific documentation
- For ML issues: Check Hugging Face and PyTorch documentation
- For health analysis: The rule-based system is always available as fallback 