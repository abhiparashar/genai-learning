# Complete Prompt Engineering Guide

## From Beginner to FAANG Interview Level

---

## TABLE OF CONTENTS

1. [What is Prompt Engineering?](#what-is-prompt-engineering)
2. [Why Companies Care](#why-companies-care)
3. [Core Concepts - The Basics](#core-concepts)
4. [The 7 Key Techniques](#the-7-key-techniques)
5. [Advanced Patterns](#advanced-patterns)
6. [Real-World Use Cases](#real-world-use-cases)
7. [Common Mistakes to Avoid](#common-mistakes)
8. [FAANG Interview Questions](#faang-interview-questions)
9. [Practice Exercises](#practice-exercises)

---

## WHAT IS PROMPT ENGINEERING?

### Simple Definition

**Prompt Engineering** = The art of writing instructions for AI models to get the best results.

Think of it like this:

- **Bad Manager**: "Do the report" → Employee confused, bad output
- **Good Manager**: "Create a 5-page sales report for Q3, include graphs, compare to Q2, highlight top 3 products" → Employee knows exactly what to do

You are the "manager" and the AI is your "employee". Better instructions = better results.

### Why It Exists

AI models like ChatGPT, Gemini, Claude are:

- Very smart but not mind readers
- Need clear instructions
- Can do MANY things, but need to know WHAT you want

**Example:**

```
❌ Bad Prompt: "Write about dogs"
✅ Good Prompt: "Write a 200-word blog post about why Golden Retrievers make great family pets. Use a friendly tone and include 3 specific benefits."
```

The AI can write about dogs in 1000 ways. Your job: Tell it WHICH way.

---

## WHY COMPANIES CARE

### In FAANG Interviews

Companies like Google, Amazon, Meta ask about prompt engineering because:

1. **Cost Savings**: Bad prompts waste API calls ($$$)

   - Bad prompt might need 5 tries
   - Good prompt works first time
   - At scale: Millions of dollars difference

2. **Product Quality**: Better prompts = Better user experience

   - Google Search AI
   - Amazon product descriptions
   - Meta's content moderation

3. **Real Job Task**: You'll write prompts daily
   - Creating AI features
   - Testing AI products
   - Building chatbots, agents, tools

### What They're Testing

- Can you think clearly?
- Can you break down problems?
- Do you understand how AI works?
- Can you optimize for cost/quality?

---

## CORE CONCEPTS

### 1. The Prompt Structure

Every prompt has parts (like a sentence has subject/verb/object):

```
[ROLE] + [TASK] + [CONTEXT] + [FORMAT] + [CONSTRAINTS]
```

**Example Breakdown:**

```
You are a Python teacher [ROLE]
Explain how loops work [TASK]
to a student who knows Java [CONTEXT]
using a simple code example [FORMAT]
in under 100 words [CONSTRAINTS]
```

### 2. Token Basics

**Token** = Piece of text AI reads/writes

- "Hello" = 1 token
- "Hello world" = 2 tokens
- "Don't" = 2 tokens (Don + 't)

**Why It Matters:**

- APIs charge per token
- Models have token limits
- Shorter prompts = cheaper, faster

**Rule of Thumb:**

- 1 token ≈ 4 characters
- 100 tokens ≈ 75 words

### 3. Temperature Setting

**Temperature** = How "creative" vs "predictable" the AI is

- **0.0 to 0.3**: Very predictable, factual, consistent
  - Use for: Math, coding, data analysis
- **0.4 to 0.7**: Balanced
  - Use for: General conversation, Q&A
- **0.8 to 1.0**: Creative, varied, surprising
  - Use for: Stories, marketing copy, brainstorming

**Example:**

```python
# Factual task
model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content(
    "What is 25 * 4?",
    generation_config={"temperature": 0.0}  # Want exact answer
)

# Creative task
response = model.generate_content(
    "Write a funny tagline for a pizza shop",
    generation_config={"temperature": 0.9}  # Want creativity
)
```

---

## THE 7 KEY TECHNIQUES

### Technique 1: Be Specific

**Problem**: Vague prompts give random results

❌ **Vague:**

```
"Write about climate change"
```

✅ **Specific:**

```
"Write a 300-word article explaining how solar panels work, targeting homeowners with no science background. Use simple analogies and include 3 benefits."
```

**Why It Works:** AI knows exactly what, how much, for whom, and what to include.

---

### Technique 2: Use System Prompts (Give AI a Role)

**System Prompt** = Telling AI "who" it is before the conversation starts

**Think of it like:**

- Hiring a professional vs asking a random person
- An accountant gives different advice than a comedian

❌ **Without Role:**

```
"How do I invest $10,000?"
```

_Result: Generic, safe, boring answer_

✅ **With Role (System Prompt):**

```python
system_instruction = "You are a financial advisor with 20 years experience, specializing in helping beginners invest safely."

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction=system_instruction
)

response = model.generate_content("How do I invest $10,000?")
```

_Result: Detailed, professional, step-by-step advice_

**Common Roles:**

- "You are an expert Python developer..."
- "You are a patient teacher..."
- "You are a creative marketing copywriter..."
- "You are a strict code reviewer..."

---

### Technique 3: Few-Shot Learning (Show Examples)

**Few-Shot** = Show AI examples of what you want

**Formula:**

```
Here are examples:
[Example 1] → [Desired Output 1]
[Example 2] → [Desired Output 2]

Now do this:
[Your Input] → ?
```

**Real Example - Sentiment Analysis:**

```
Analyze sentiment as positive, negative, or neutral.

Examples:
"I love this product!" → Positive
"Terrible experience, never again." → Negative
"It's okay, nothing special." → Neutral

Now analyze:
"Best purchase I've made all year!" → ?
```

_AI will respond: Positive_

**Why It Works:** AI learns your pattern and follows it.

**Use Cases:**

- Data formatting
- Classification tasks
- Specific writing styles
- Custom output formats

---

### Technique 4: Chain of Thought (CoT)

**CoT** = Ask AI to "think step-by-step" before answering

**The Magic Phrase:** "Let's think step by step"

❌ **Without CoT:**

```
"If a train travels 60 mph for 2.5 hours, then 80 mph for 1.5 hours, how far did it go?"
```

_AI might give wrong answer: 350 miles_

✅ **With CoT:**

```
"If a train travels 60 mph for 2.5 hours, then 80 mph for 1.5 hours, how far did it go?

Let's think step by step:"
```

_AI responds:_

```
Step 1: Calculate first distance: 60 mph × 2.5 hours = 150 miles
Step 2: Calculate second distance: 80 mph × 1.5 hours = 120 miles
Step 3: Add them together: 150 + 120 = 270 miles
Answer: 270 miles
```

**When to Use:**

- Math problems
- Logic puzzles
- Complex reasoning
- Multi-step tasks
- Debugging code

---

### Technique 5: Output Formatting

**Tell AI exactly how you want the output structured**

**Common Formats:**

- JSON
- Markdown table
- Bullet points
- CSV
- HTML
- Step-by-step numbered list

**Example - Getting Structured Data:**

```
Extract information from this text and return as JSON:
"John Smith, age 32, works at Google as a Software Engineer. Email: john@example.com"

Return format:
{
  "name": "",
  "age": 0,
  "company": "",
  "role": "",
  "email": ""
}
```

**Example - Table Format:**

```
Compare Python, Java, and JavaScript in a markdown table with these columns:
- Language
- Use Case
- Difficulty
- Popularity

Format as:
| Language | Use Case | Difficulty | Popularity |
|----------|----------|------------|------------|
```

**Why It Matters:**

- Easy to parse programmatically
- Consistent outputs
- Integration with other systems

---

### Technique 6: Constraints & Guardrails

**Constraints** = Rules AI must follow

**Types of Constraints:**

**1. Length Constraints:**

```
"Explain quantum computing in exactly 50 words"
"Write a tweet (under 280 characters) about AI safety"
```

**2. Style Constraints:**

```
"Explain like I'm 5 years old"
"Use formal business language"
"Write in the style of a news article"
```

**3. Content Constraints:**

```
"Don't use technical jargon"
"Only use information from the provided context"
"Do not make up information - say 'I don't know' if unsure"
```

**4. Safety Constraints:**

```
"Only generate SELECT queries, never DELETE or DROP"
"Don't include personal information"
"Avoid controversial topics"
```

**Real Example - SQL Safety:**

```
You are a SQL query generator. Rules:
1. Only generate SELECT queries
2. Never use DELETE, DROP, UPDATE, or INSERT
3. If user asks for these, respond: "I can only help with read queries"

Convert to SQL: "Show me all customers from California"
```

---

### Technique 7: Iterative Refinement

**Start broad, then refine based on output**

**Process:**

```
Prompt v1 → Review output → Improve prompt → Prompt v2 → Better output
```

**Example Iteration:**

**Prompt v1:**

```
"Write a product description for headphones"
```

_Output: Too generic_

**Prompt v2:**

```
"Write a 100-word product description for noise-canceling wireless headphones, targeting remote workers. Highlight: battery life, comfort, and focus benefits."
```

_Output: Better but too formal_

**Prompt v3:**

```
"Write a 100-word product description for noise-canceling wireless headphones, targeting remote workers. Highlight: battery life, comfort, and focus benefits. Use conversational tone with personal pronouns (you, your). Include one emotional benefit."
```

_Output: Perfect!_

**Key Point:** Prompting is experimental. Test and improve.

---

## ADVANCED PATTERNS

### Pattern 1: Prompt Chaining

**Break complex tasks into multiple prompts**

**Example - Writing a Blog Post:**

```
Prompt 1: "Generate 5 blog post titles about AI in healthcare"
→ Get titles

Prompt 2: "For the title '[selected title]', create an outline with 5 sections"
→ Get outline

Prompt 3: "Write the introduction section (200 words) based on this outline: [paste outline]"
→ Get intro

Prompt 4: "Write section 2 based on this outline..."
→ Continue
```

**Why It Works:**

- More control over each step
- Better quality outputs
- Easier to fix issues
- Can save/reuse steps

---

### Pattern 2: Self-Consistency

**Ask same question multiple times, pick best answer**

**Example - Code Review:**

```python
# Ask 3 times with temperature 0.7
reviews = []
for i in range(3):
    response = model.generate_content(
        "Review this code for bugs: [code]",
        generation_config={"temperature": 0.7}
    )
    reviews.append(response.text)

# Compare and pick most thorough review
```

**Use When:**

- Critical decisions
- Need diverse perspectives
- Want to catch edge cases

---

### Pattern 3: Meta-Prompting

**Ask AI to improve your prompt**

**Example:**

```
I want to create a prompt that generates professional email responses. Here's my current prompt:

"Write an email response"

Please improve this prompt to be more effective. Consider:
- Role definition
- Context needed
- Output format
- Constraints

Provide the improved prompt.
```

**AI might suggest:**

```
You are a professional executive assistant. Write a polite email response based on:
- The incoming email: [paste email]
- Desired action: [accept/decline/request info]
- Tone: [formal/friendly/brief]

Format:
- Subject line
- Greeting
- 2-3 sentence body
- Professional closing
- Keep under 150 words
```

---

### Pattern 4: Context Stuffing

**Provide relevant information in the prompt**

**Example - Customer Support:**

```
Context: You are helping customer #12345
- Name: Sarah Johnson
- Issue: Can't login
- Account type: Premium
- Last login: 2 days ago
- Browser: Chrome
- Previous tickets: 0

Based on this context, provide step-by-step troubleshooting instructions.
```

**Why It Works:**

- AI has all needed information
- Personalized responses
- No hallucination (making up facts)

---

## REAL-WORLD USE CASES

### Use Case 1: Text-to-SQL Agent

**Problem:** Convert questions to SQL safely

**Prompt Pattern:**

```python
system_prompt = """You are a SQL expert. Generate safe SQL queries.

Rules:
1. Only SELECT queries allowed
2. Use provided table schema
3. Add LIMIT 100 to all queries
4. If unsafe request, return: {"error": "Cannot perform this action"}

Available tables:
- customers (id, name, email, city, signup_date)
- orders (id, customer_id, product, amount, order_date)
- products (id, name, price, category)

Return format:
{
  "sql": "SELECT ...",
  "explanation": "This query..."
}
"""

user_question = "Show me customers from California who ordered in 2024"
```

---

### Use Case 2: RAG System (Document Q&A)

**Problem:** Answer questions from your documents

**Prompt Pattern:**

```python
prompt = f"""Answer the question based ONLY on the provided context. If the answer isn't in the context, say "I don't know based on the provided information."

Context:
{retrieved_document_chunks}

Question: {user_question}

Answer:"""
```

---

### Use Case 3: Code Review Agent

**Prompt Pattern:**

```python
system_prompt = """You are a senior software engineer conducting code review.

Review checklist:
1. Bugs and logic errors
2. Security vulnerabilities
3. Performance issues
4. Code style and readability
5. Missing error handling

For each issue found:
- Severity: Critical/High/Medium/Low
- Line number
- Explanation
- Suggested fix

If code is perfect, say "LGTM - No issues found"
"""
```

---

### Use Case 4: Content Generation Pipeline

**Multi-step process:**

```python
# Step 1: Generate ideas
ideas_prompt = "Generate 10 blog post ideas about Python for beginners"

# Step 2: Pick best idea
selection_prompt = f"From these ideas: {ideas}, pick the most useful for a Java developer learning Python. Explain why."

# Step 3: Create outline
outline_prompt = f"Create a detailed outline for: {selected_idea}"

# Step 4: Write sections
for section in outline:
    content_prompt = f"Write {section} in 300 words, conversational tone, include code examples"
```

---

## COMMON MISTAKES

### Mistake 1: Being Too Vague

❌ "Write code"
✅ "Write a Python function that takes a list of numbers and returns the average"

### Mistake 2: Not Setting Constraints

❌ "Explain neural networks"
_Gets 5000 word response_

✅ "Explain neural networks in 100 words for a beginner"

### Mistake 3: Ignoring Output Format

❌ Parsing inconsistent free text
✅ Request JSON/CSV format

### Mistake 4: No Error Handling in Prompts

❌ Assuming AI always succeeds
✅ "If you can't answer, respond with: ERROR: [reason]"

### Mistake 5: Not Testing with Edge Cases

❌ Only test happy path
✅ Test with:

- Empty inputs
- Very long inputs
- Special characters
- Ambiguous questions

### Mistake 6: Overcomplicating

❌ 500-word prompt with 20 rules
✅ Simple, clear instructions

**Rule:** Start simple, add complexity only if needed

---

## FAANG INTERVIEW QUESTIONS

### Question 1: Token Optimization

**Q:** "You have a prompt that costs $0.50 per API call because it's too long. How would you optimize it?"

**Answer:**

```
1. Remove redundant instructions
2. Use abbreviations where clear (e.g., "e.g." vs "for example")
3. Move examples to few-shot format (more efficient)
4. Use bullet points vs paragraphs
5. Cache system prompts (reuse across calls)
6. Compress context (summarize long documents first)

Example:
Before (200 tokens):
"I would like you to please analyze the following customer review and tell me whether the sentiment expressed in the review is positive, negative, or neutral..."

After (50 tokens):
"Sentiment analysis (positive/negative/neutral):
Review: [text]"
```

---

### Question 2: Consistency Problem

**Q:** "Your AI chatbot gives different answers to the same question. How do you fix this?"

**Answer:**

```
1. Set temperature = 0.0 for deterministic outputs
2. Use detailed prompts (less ambiguity)
3. Add output format constraints
4. Implement prompt caching
5. Use few-shot examples
6. Add "Always respond in this format..." instruction

Code example:
generation_config = {
    "temperature": 0.0,  # Deterministic
    "top_p": 1.0,
    "top_k": 1
}
```

---

### Question 3: Safety & Security

**Q:** "Design a prompt that prevents SQL injection via natural language"

**Answer:**

```python
system_prompt = """You are a SQL generator with strict safety rules.

ALLOWED: Only SELECT queries
FORBIDDEN: DELETE, DROP, UPDATE, INSERT, ALTER, EXEC, UNION, --

Validation:
1. If user asks for forbidden operations, return:
   {"error": "Operation not allowed", "reason": "..."}
2. Always use parameterized queries
3. Add LIMIT clause (max 1000 rows)
4. Escape special characters

Example safe query:
Input: "Show users named John"
Output: SELECT * FROM users WHERE name = ? LIMIT 1000
Parameters: ["John"]

If query seems malicious (e.g., "'; DROP TABLE"), return error.
"""
```

---

### Question 4: Cost vs Quality Tradeoff

**Q:** "You need to process 1 million customer reviews. Using GPT-4 ($30/million tokens) vs GPT-3.5 ($0.50/million tokens). How do you decide?"

**Answer:**

```
Strategy: Hybrid approach

1. Use cheap model (GPT-3.5) for initial filtering
   - Simple sentiment: positive/negative/neutral
   - Cost: $0.50 per million

2. Use expensive model (GPT-4) only for:
   - Neutral cases (need deeper analysis)
   - Critical issues
   - Complex reviews
   - ~10% of total

3. Calculate:
   - 900k reviews @ $0.50 = $0.45
   - 100k reviews @ $30 = $3.00
   - Total: $3.45 vs $30 (88% savings)

4. Monitor quality:
   - Sample check accuracy
   - Adjust threshold if needed
```

---

### Question 5: Hallucination Prevention

**Q:** "Your AI makes up facts. How do you fix this?"

**Answer:**

```
Techniques:

1. Explicit instructions:
   "Only use information from the provided context. If you don't know, say 'I don't have this information.'"

2. RAG (Retrieval Augmented Generation):
   - Fetch relevant docs first
   - Include in prompt
   - Ground responses in facts

3. Fact-checking prompt:
   "For each claim, cite the source: [claim] (Source: document X, page Y)"

4. Lower temperature (0.0-0.3):
   - More factual
   - Less creative guessing

5. Structured output:
   {
     "answer": "...",
     "confidence": "high/medium/low",
     "sources": [...]
   }

6. Two-step verification:
   - Generate answer
   - Verify against source
   - Only return if verified
```

---

### Question 6: Multi-Language Support

**Q:** "Design a prompt for a customer support bot that works in 50+ languages"

**Answer:**

```python
system_prompt = """You are a multilingual customer support agent.

Instructions:
1. Detect user's language automatically
2. Respond in the SAME language
3. Maintain consistent tone across languages
4. Use formal language unless user is casual

Format:
{
  "detected_language": "es",
  "response": "...",
  "translated_to_english": "..." // for logging
}

Examples:
User: "¿Dónde está mi pedido?" (Spanish)
You: Respond in Spanish

User: "Where is my order?" (English)
You: Respond in English

Quality checks:
- Maintain cultural appropriateness
- Adjust formality per language norms
- Use local date/time formats
"""
```

---

### Question 7: A/B Testing Prompts

**Q:** "You want to improve your prompts. How do you A/B test them scientifically?"

**Answer:**

```
Process:

1. Define success metric:
   - Task completion rate
   - User satisfaction score
   - Response accuracy
   - Time to complete

2. Create variants:
   Prompt A (current):
   "Summarize this article"

   Prompt B (test):
   "Summarize this article in 3 bullet points, each under 20 words, focusing on key facts"

3. Split traffic:
   - 50% users get Prompt A
   - 50% users get Prompt B
   - Run for 1 week or 1000 samples

4. Measure:
   - Prompt A: 75% accuracy, 8/10 satisfaction
   - Prompt B: 85% accuracy, 9/10 satisfaction

5. Statistical significance:
   - Use Chi-square test
   - p-value < 0.05 = significant

6. Deploy winner:
   - Roll out Prompt B to 100%

7. Continuous improvement:
   - Test new variant vs current winner
   - Repeat cycle
```

---

## PRACTICE EXERCISES

### Exercise 1: Basic Prompt Writing

**Task:** Write a prompt to extract structured data

**Input Text:**
"Meeting scheduled for next Monday at 2 PM with John Smith and Sarah Connor to discuss Q4 budget. Location: Conference Room B."

**Your Task:** Write a prompt that extracts:

- Date & Time
- Attendees
- Topic
- Location

**Return as JSON**

---

### Exercise 2: Few-Shot Learning

**Task:** Create a few-shot prompt for email classification

**Categories:** Urgent, Normal, Spam

**Provide 2 examples for each category, then classify:**
"Your account will be suspended in 24 hours. Click here to verify."

---

### Exercise 3: Chain of Thought

**Task:** Write a CoT prompt for this problem:

"A store sells apples for $2 each, but offers 20% off if you buy 10 or more. You buy 15 apples. How much do you pay?"

Make the AI show step-by-step reasoning.

---

### Exercise 4: Safety Constraints

**Task:** Write a prompt for a recipe generator that:

- Never suggests allergenic ingredients (nuts, shellfish)
- Always asks about dietary restrictions first
- Provides calorie count
- Warns about cooking dangers (hot oil, sharp knives)

---

### Exercise 5: Real-World Scenario

**Task:** You're building a code review bot. Write a complete prompt that:

1. Reviews Python code for:

   - Bugs
   - Security issues
   - Performance problems
   - Style violations

2. Returns structured output:

   ```json
   {
     "issues": [
       {
         "line": 5,
         "severity": "high",
         "type": "security",
         "description": "...",
         "fix": "..."
       }
     ],
     "score": 75,
     "summary": "..."
   }
   ```

3. If code is perfect: score = 100, issues = []

---

## QUICK REFERENCE CHEAT SHEET

### When to Use Each Technique

| Technique        | Use When              | Example                         |
| ---------------- | --------------------- | ------------------------------- |
| Be Specific      | Always                | Every prompt                    |
| System Prompt    | Role/persona needed   | Chatbots, assistants            |
| Few-Shot         | Pattern needed        | Classification, formatting      |
| Chain of Thought | Complex reasoning     | Math, logic, debugging          |
| Output Format    | Need structured data  | JSON, tables, lists             |
| Constraints      | Safety/quality needed | SQL generation, content filters |
| Prompt Chaining  | Multi-step task       | Research, content creation      |

### Quick Checklist for Good Prompts

✅ Clear task description
✅ Role/context provided
✅ Output format specified
✅ Constraints mentioned
✅ Examples included (if needed)
✅ Edge cases considered
✅ Success criteria defined

---

## NEXT STEPS

Now that you understand prompt engineering:

1. **Practice** with exercises above
2. **Apply** to Text-to-SQL project
3. **Experiment** with different patterns
4. **Measure** what works best
5. **Iterate** and improve

**Remember:**

- Prompting is a skill (practice makes perfect)
- No "perfect" prompt (context matters)
- Test with real users/data
- Simple often beats complex

---

## RESOURCES

**Practice:**

- Try prompts with Gemini API
- Build small projects
- Experiment with temperature

**Learn More:**

- Anthropic Prompt Library: https://docs.anthropic.com/claude/prompt-library
- OpenAI Prompt Engineering Guide: https://platform.openai.com/docs/guides/prompt-engineering
- LangChain Prompts: https://python.langchain.com/docs/modules/model_io/prompts/

**Keep Learning:**

- Test different models
- Read others' prompts
- Share and get feedback

---

**YOU'RE NOW READY FOR:**
✅ FAANG interviews about prompt engineering
✅ Building production AI applications
✅ Optimizing AI costs and quality
✅ Designing complex AI systems

**NEXT PROJECT: Text-to-SQL Agent** 🚀

---

_Created for: Java developer learning GenAI_
_Goal: Practical knowledge for getting hired_
_Date: 2025_
