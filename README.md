# AI Content Generator

This project is a simple web app that uses AI (Mistral Small 3.1 via OpenRouter API) to automatically generate blog articles based on any given topic.

## How to Run

1. Install libraries:
    pip install -r requirements.txt

2. Replace your OpenRouter API Key in generator.py

3. Start the app:
    python app.py

4. Open browser: http://127.0.0.1:5000/

## Features

- Topic-based article generation
- Save generated content to `generated_article.txt`
- Simple Flask web interface
