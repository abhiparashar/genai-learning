import google.generativeai as genai
import json

API_KEY = "API_KEY"
genai.configure(api_key=API_KEY)

def classify_email(email_text):
    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = """
You are an email classification assistant. Classify emails in category and urgency levels.

CATEGORIES: Support, Sales, Spam
URGENCY LEVELS: High, Medium, Low

Here are some examples:
Example 1:
Email: "Hi, I'm interested in your premium plan. Can you send me pricing details and schedule a demo for next week?"
Output: {"category": "Sales", "urgency": "Medium"}

Example 2:
Email: "URGENT! Your account has been compromised. Click here immediately to verify your identity and claim your prize!"
Output: {"category": "Spam", "urgency": "Low"}

Example 3:
Email: "Our production server is down and customers can't access the application. We need immediate assistance!"
Output: {"category": "Support", "urgency": "High"}

Example 4:
Email: "Hello, I have a question about how to export data from my dashboard. It's not urgent, just when you have time."
Output: {"category": "Support", "urgency": "Low"}

Example 5:
Email: "We'd like to upgrade our subscription plan from Basic to Enterprise. Please send us the details."
Output: {"category": "Sales", "urgency": "Medium"}

Now classify this email:
Email: """ + email_text + """
Output (JSON format only, no explanation):

"""
    # Generate response
    response = model.generate_content(prompt)
    try:
        # Parse JSON response
        result = json.loads(response.text.strip())
        return result       
    except json.JSONDecodeError:
        # If response isn't valid JSON, try to extract it
        text = response.text.strip()
        # Remove markdown code blocks if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```":
            text = text.split("```")[1].split["```"][0].strip()

        try:
            result = json.loads(text)
            return result
        except:
            return {"category": "Unknown", "urgency": "Unknown", "raw_response": response.text}
    


def main():
     # Test cases
    test_emails = [
        "CRITICAL: Our payment gateway is failing. Customers cannot complete purchases. This is costing us thousands of dollars per hour. Need immediate fix!",
        "Hi team, I'm from Acme Corp. We have 500 employees and are looking for an enterprise solution. Could we schedule a call to discuss pricing and features?",
        "Congratulations!!! You've WON $1,000,000! Click here NOW to claim your prize before it expires! Limited time offer!!!",
        "Hey, I was wondering if there's a way to change the color theme in the settings. No rush, just curious about this feature."
    ]

    for email in test_emails:
        result = classify_email(email)
        print(f"Email: {email[:60]}...")
        print(f"Result: {json.dumps(result)}\n")

if __name__=="__main__":
    main()

