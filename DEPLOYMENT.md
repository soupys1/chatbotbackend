# Health Chatbot Backend - Render Deployment Guide

## Overview
This guide will help you deploy the Health Chatbot backend to Render.com.

## Prerequisites
- A Render.com account
- Git repository with your backend code
- Python 3.11+ (Render will handle this)

## Deployment Steps

### 1. Prepare Your Repository
Ensure your backend directory contains:
- `app.py` - Main Flask application
- `requirements.txt` - Python dependencies
- `render.yaml` - Render configuration
- `models/` - Health analyzer models
- `.gitignore` - Git ignore rules

### 2. Deploy to Render

#### Option A: Using render.yaml (Recommended)
1. Push your code to GitHub/GitLab
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click "New +" → "Web Service"
4. Connect your repository
5. Render will automatically detect the `render.yaml` configuration
6. Click "Create Web Service"

#### Option B: Manual Configuration
1. Push your code to GitHub/GitLab
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click "New +" → "Web Service"
4. Connect your repository
5. Configure manually:
   - **Name**: `health-chatbot-backend`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Plan**: `Free`

### 3. Environment Variables
Set these in Render dashboard:
- `PORT`: `10000` (Render will override)
- `ENABLE_ML_MODELS`: `false` (for free tier)
- `DEBUG`: `false` (for production)

### 4. Health Check
The service includes a health check endpoint at `/health` that Render will use to verify the service is running.

## Configuration Files

### render.yaml
```yaml
services:
  - type: web
    name: health-chatbot-backend
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py
    envVars:
      - key: PORT
        value: 10000
      - key: ENABLE_ML_MODELS
        value: false
      - key: PYTHON_VERSION
        value: 3.11
    healthCheckPath: /health
```

### requirements.txt
Contains all necessary Python dependencies with specific versions for stability.

## Testing Before Deployment

### Local Testing
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the backend:
   ```bash
   python app.py
   ```

3. Test the endpoints:
   ```bash
   python test_deployment.py
   ```

### API Endpoints
- `GET /health` - Health check
- `POST /analyze-health` - Single health analysis
- `POST /analyze-health-batch` - Batch health analysis
- `POST /analyze-health-file` - CSV file analysis

## Troubleshooting

### Common Issues

#### 1. Build Failures
- Check `requirements.txt` for correct package versions
- Ensure all dependencies are compatible
- Check Render logs for specific error messages

#### 2. Runtime Errors
- Verify environment variables are set correctly
- Check that the health analyzer loads properly
- Review application logs in Render dashboard

#### 3. Memory Issues (Free Tier)
- Set `ENABLE_ML_MODELS=false` to use rule-based analysis only
- Reduce batch processing limits
- Monitor memory usage in Render dashboard

### Logs and Monitoring
- View logs in Render dashboard under your service
- Monitor health check status
- Check for any error messages during startup

## Performance Optimization

### For Free Tier
- Disable ML models (`ENABLE_ML_MODELS=false`)
- Use rule-based analysis only
- Limit batch processing to 20 items max
- Keep file uploads under 50 rows

### For Paid Tiers
- Enable ML models for better accuracy
- Increase batch processing limits
- Add more memory and CPU resources

## Security Considerations
- CORS is enabled for frontend integration
- Input validation on all endpoints
- File upload restrictions (CSV only)
- Rate limiting recommended for production

## Updating the Deployment
1. Push changes to your Git repository
2. Render will automatically redeploy
3. Monitor the deployment logs
4. Test the updated endpoints

## Support
If you encounter issues:
1. Check Render documentation
2. Review application logs
3. Test locally first
4. Verify all configuration files are correct 