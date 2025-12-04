import google.generativeai as genai
import json
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def analyze_sentiment(review):
    """
    Analyze sentiment of a customer review
    Returns: sentiment, confidence, and key points
    """
    
    prompt = f"""
You are a sentiment analysis system for product reviews.

Analyze this review and return ONLY valid JSON (no markdown, no extra text):

Review: "{review}"

Return this exact JSON format:
{{
  "sentiment": "positive" or "negative" or "neutral",
  "confidence": 0.0 to 1.0,
  "key_points": ["point1", "point2", "point3"],
  "recommendation": "brief action recommendation"
}}

Think step by step:
1. Read the entire review
2. Identify positive phrases (great, love, excellent, etc.)
3. Identify negative phrases (terrible, disappointed, poor, etc.)
4. Determine overall sentiment
5. Assess confidence based on clarity of sentiment
6. Extract 2-3 key points mentioned
"""
    response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=0,top_p=0.90, top_k=40))
    # Parse JSON from response
    try:
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
                text = text.strip()
        result = json.loads(text)
        return result
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print(f"Raw response: {response.text}")
        return None
    
def main():
    print("=" * 60)
    print("SENTIMENT ANALYZER")
    print("=" * 60)
    print()
     # Test cases
    test_reviews = [
        "This product is absolutely amazing! Best purchase I've ever made. The quality is outstanding and shipping was super fast. Highly recommend!",
        
        "Terrible experience. Product arrived damaged and customer service was unhelpful. Would not recommend to anyone. Complete waste of money.",
        
        "Product is okay. Does what it's supposed to do but nothing special. Shipping took a while but eventually arrived. Average overall.",
        
        "I love the design but the quality is disappointing. It broke after just 2 weeks. The price was good though.",
        
        "Fast shipping and good packaging. Product works perfectly. Very satisfied with my purchase!"
    ]

    for i,review in enumerate(test_reviews,1):
        print(f"Review {i}:")
        print(f'"{review}"')
        print()
        result = analyze_sentiment(review)
         
        if result:
            print(f"Sentiment: {result['sentiment'].upper()}")
            print(f"Confidence: {result['confidence']:.1%}")
            print(f"Key Points:")
            for point in result['key_points']:
                print(f"  • {point}")
            print(f"Recommendation: {result['recommendation']}")
        
        print()
        print("-" * 60)
        print()

if __name__ == "__main__":
    main()