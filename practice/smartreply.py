import google.generativeai as genai
import json

genai.configure(api_key="API_KEY")

def generate_smart_replies(email_subject, email_content):
    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = f"""
You are an automatic email reply assistant. you need to read content and reply of it.
Given the email below, generate 3 different reply options:

1. **FORMAL**: Professional, detailed, suitable for business/corporate context
2. **CASUAL**: Friendly, conversational, suitable for colleagues or informal business
3. **BRIEF**: Short and concise, gets straight to the point

Important:
- Make replies contextually appropriate to the email content
- Include relevant details from the original email
- Use proper email etiquette
- Keep brief reply under 3 sentences
- Add appropriate greetings and signatures
- Return ONLY the JSON, no additional text

For each reply, provide:
- Subject line (starting with "Re: ")
- Email body

Original Email Subject: {email_subject if email_subject else "No subject"}
Email Content:
{email_content}
Generate the replies in the following JSON format:
{{
  "formal": {{
    "subject": "Re: ...",
    "body": "..."
  }},
  "casual": {{
    "subject": "Re: ...",
    "body": "..."
  }},
  "brief": {{
    "subject": "Re: ...",
    "body": "..."
  }}
}}
"""
    response = model.generate_content(prompt)
    try:
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        result = json.loads(text)
        return result
    except json.JSONDecodeError as e:
         return {
            "error": f"Failed to parse response: {str(e)}",
            "raw_response": response.text
        }
    


def display_replies(email_content, replies):
    print(f"\nOriginal Email: {email_content[:100]}...\n")
    
    if "error" in replies:
        print(f"Error: {replies['error']}")
        return
    
    print("FORMAL REPLY:")
    print(f"Subject: {replies['formal']['subject']}")
    print(replies['formal']['body'])
    print()
    
    print("CASUAL REPLY:")
    print(f"Subject: {replies['casual']['subject']}")
    print(replies['casual']['body'])
    print()
    
    print("BRIEF REPLY:")
    print(f"Subject: {replies['brief']['subject']}")
    print(replies['brief']['body'])
    print("\n" + "-" * 80)


def main():
    # Test cases
    test_emails = [
        {
            "subject": "Quick sync on Q4 project",
            "content": "Hi there,\n\nHope you're doing well! I wanted to touch base about the Q4 marketing campaign. We've made some changes to the timeline and I think it would be great to sync up this week.\n\nAre you available for a 30-minute call on Thursday or Friday afternoon? Let me know what works best for you.\n\nThanks!\nSarah"
        }
    ]

    for email in test_emails:
        response =  generate_smart_replies(email['subject'],email['content'])
        display_replies(email['content'], response)


if __name__ == "__main__":
    main()

