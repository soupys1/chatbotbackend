# AI Health Assistant Chatbot

A comprehensive health analysis system that can understand user health issues and provide personalized health advice and recommendations.

## Features

- **Health Issue Analysis**: Analyzes user health concerns and symptoms
- **Emergency Detection**: Identifies emergency situations requiring immediate medical attention
- **Health Category Classification**: Categorizes issues into physical symptoms, mental health, chronic conditions, and lifestyle
- **Personalized Health Advice**: Provides specific, actionable health recommendations
- **Urgency Assessment**: Determines the urgency level of health concerns
- **Sentiment Analysis**: Understands the emotional context of health concerns

## System Architecture

### Backend (Flask API)
- **Health Analyzer**: Advanced AI model for health issue analysis
- **Emergency Detection**: Real-time emergency situation identification
- **Health Advice Generation**: Contextual health recommendations
- **Batch Processing**: Support for analyzing multiple health concerns

### Frontend (React)
- **Modern Chat Interface**: Clean, intuitive health consultation interface
- **Real-time Analysis**: Instant health analysis and advice
- **Emergency Warnings**: Prominent emergency alerts when needed
- **Health Category Visualization**: Visual representation of detected health areas

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the Flask server:
```bash
python app.py
```

The backend will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend/vite-project
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## API Endpoints

### Health Analysis
- `POST /analyze-health` - Analyze single health concern
- `POST /analyze-health-batch` - Analyze multiple health concerns
- `POST /analyze-health-file` - Analyze health concerns from CSV file

### Legacy Endpoints (Backward Compatibility)
- `POST /analyze` - Legacy sentiment analysis (now provides health analysis)
- `POST /analyze-batch` - Legacy batch analysis

### Health Check
- `GET /health` - API health status

## Usage Examples

### Single Health Analysis
```bash
curl -X POST http://localhost:5000/analyze-health \
  -H "Content-Type: application/json" \
  -d '{"text": "I have been experiencing headaches and fatigue for the past week"}'
```

### Batch Health Analysis
```bash
curl -X POST http://localhost:5000/analyze-health-batch \
  -H "Content-Type: application/json" \
  -d '{"texts": ["I have a headache", "I feel anxious", "I want to improve my diet"]}'
```

## Health Categories

The system can analyze and provide advice for:

### Physical Symptoms
- Headaches, fever, cough, sore throat
- Nausea, vomiting, diarrhea
- Fatigue, dizziness, chest pain
- Shortness of breath, back pain, joint pain
- Muscle pain, abdominal pain, rash, swelling

### Mental Health
- Anxiety, depression, stress
- Panic, worry, sadness, hopelessness
- Irritability, mood swings, insomnia
- Concentration issues, memory problems
- Suicidal thoughts, self-harm concerns

### Chronic Conditions
- Diabetes, hypertension, asthma
- Arthritis, heart disease, cancer
- Thyroid issues, kidney disease
- Liver disease, autoimmune conditions

### Lifestyle
- Diet and nutrition
- Exercise and fitness
- Weight management
- Smoking, alcohol consumption
- Sleep patterns

## Emergency Detection

The system automatically detects emergency situations including:
- Chest pain or heart attack symptoms
- Stroke symptoms
- Severe bleeding
- Unconsciousness
- Difficulty breathing
- Severe head injury
- Suicidal thoughts
- Severe allergic reactions

## Health Advice Features

- **Contextual Recommendations**: Advice tailored to specific symptoms
- **Lifestyle Guidance**: Diet, exercise, and wellness recommendations
- **Professional Referral**: When to consult healthcare providers
- **Emergency Protocols**: Immediate action steps for urgent situations
- **Preventive Care**: Proactive health maintenance suggestions

## Safety and Disclaimers

⚠️ **Important**: This AI health assistant is designed to provide general health information and guidance only. It is not a substitute for professional medical advice, diagnosis, or treatment.

- Always consult with qualified healthcare professionals for medical concerns
- In emergency situations, call emergency services immediately
- The system's recommendations should not replace professional medical care
- Use this tool as a supplement to, not replacement for, professional healthcare

## Technical Details

### AI Models Used
- **Sentiment Analysis**: RoBERTa-based sentiment classification
- **Health Classification**: Zero-shot text classification for health topics
- **Emergency Detection**: Keyword-based emergency situation identification

### Performance Features
- Real-time analysis with response times under 2 seconds
- Batch processing for multiple health concerns
- CSV file upload support for bulk analysis
- Comprehensive error handling and logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For technical support or questions about the health chatbot system, please open an issue in the repository. 