# generator.py
from openai import OpenAI
import time

# Initialize OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",  # Replace with your key
)

# List of supported models
supported_models = [
    {"id": "mistralai/mistral-small-3.1-24b-instruct:free", "name": "Mistral Small 3.1", "free": True},
    {"id": "anthropic/claude-3-haiku:free", "name": "Claude 3 Haiku", "free": True},
    {"id": "google/gemma-7b-it:free", "name": "Gemma 7B", "free": True},
    {"id": "mistralai/mistral-large-2402:pro", "name": "Mistral Large (Pro Only)", "free": False},
    {"id": "anthropic/claude-3-opus:pro", "name": "Claude 3 Opus (Pro Only)", "free": False},
    {"id": "meta-llama/llama-3-70b-instruct:pro", "name": "Llama 3 70B (Pro Only)", "free": False},
]

def generate_content(topic, word_count=500, model="mistralai/mistral-small-3.1-24b-instruct:free", tone="informative"):
    # Set the prompt based on tone and word count
    prompts = {
        "informative": f"Write a detailed, factual blog article about: {topic}. The article should be approximately {word_count} words and use an informative, educational tone.",
        "persuasive": f"Write a persuasive blog article about: {topic}. Make compelling arguments and include a call to action. The article should be approximately {word_count} words.",
        "creative": f"Write a creative and engaging blog article about: {topic}. Use storytelling techniques and vivid imagery. The article should be approximately {word_count} words.",
        "technical": f"Write a technical blog article about: {topic} with detailed explanations and examples. The article should be approximately {word_count} words and assume the reader has some background knowledge.",
        "casual": f"Write a casual, conversational blog article about: {topic}. Use a friendly tone as if you're talking to a friend. The article should be approximately {word_count} words."
    }
    
    prompt = prompts.get(tone, prompts["informative"])
    
    # Add structure guidance
    prompt += " Include an introduction, several main sections with headings, and a conclusion."

    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional content writer who creates well-structured, engaging blog articles."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000 if model.endswith(":pro") else 1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                raise Exception(f"Failed to generate content after {max_retries} attempts: {str(e)}")

def analyze_content(text):
    """Analyze the generated content for basic metrics"""
    words = len(text.split())
    sentences = len(text.split('.'))
    avg_sentence_length = words / max(sentences, 1)
    
    return {
        "word_count": words,
        "sentence_count": sentences,
        "avg_sentence_length": round(avg_sentence_length, 1)
    }