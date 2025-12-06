import google.generativeai as genai
import os
import re

class MathProblemSolver:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def _extract_answer(self, text):
        patterns = [
            r"FINAL ANSWER:\s*(.+?)(?:\n|$)",
            r"Final [Aa]nswer:\s*(.+?)(?:\n|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return text.strip().split('\n')[-1]    

    def solve_without_cot(self, problem):
       prompt = f"{problem}\n\nGive only the final answer, no explanation or steps:"
       response = self.model.generate_content(prompt)
       return {
           'response':response.text,
           'answer':self._extract_answer(response.text)
       }
    
    def solve_with_cot(self, problem):
        prompt = f"""Solve this problem step by step.

Problem: {problem}

Let's think step by step:
1. Identify what we know and what we need to find
2. Set up the equations or relationships
3. Solve step by step, showing all work
4. State the final answer clearly

Begin:"""
        response = self.model.generate_content(prompt)
        return{
            'response': response.text,
            'answer': self._extract_answer(response.text)
        }

def main():
    solver = MathProblemSolver()

    problems = [
        "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost?",
        "If it takes 5 machines 5 minutes to make 5 widgets, how long would it take 100 machines to make 100 widgets?",
        "In a lake, there is a patch of lily pads. Every day, the patch doubles in size. If it takes 48 days for the patch to cover the entire lake, how long would it take for the patch to cover half of the lake?"
    ]

    for i, problem in enumerate(problems,1):
        print(f"\nProblem {i}: {problem}\n")
        
        no_cot = solver.solve_without_cot(problem)
        print("WITHOUT CoT:")
        print(no_cot['response'])
        print(f"Answer: {no_cot['answer']}\n")
        
        cot = solver.solve_with_cot(problem)
        print("WITH CoT:")
        print(cot['response'])
        print(f"Answer: {cot['answer']}")

if __name__ == "__main__":
    main()