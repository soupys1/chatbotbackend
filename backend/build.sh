#!/bin/bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Pre-download RoBERTa model during build (speeds up startup)
python -c "
from transformers import pipeline
print('Pre-downloading RoBERTa model...')
pipeline('sentiment-analysis', model='cardiffnlp/twitter-roberta-base-sentiment-latest')
print('Model downloaded successfully!')
"