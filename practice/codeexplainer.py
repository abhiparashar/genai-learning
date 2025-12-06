import google.generativeai as genai


genai.configure(api_key="API_KEY")

def explain_code(java_code):
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"""
You are a patient programming java teacher. you need to explain the code to beginners.
Analyze this Java code and provide:
1. Overview - what does this case do ( 1-2 lines)
2. Step-by-step breakdown - explain code line by line in simple terms
3. Key concepts - List the programming concepts used (e.g., loops, conditionals, methods)
4. Real-world analogy - Explain it using a real-world comparison that a beginner would understand
5. Use simple language. Avoid jargon. If you must use technical terms, explain them.
6. if code is of language other than politrly say no
Java code: 
{java_code}
Exaplanation: 
"""
    response = model.generate_content(prompt)
    return response.text

def format_output(code, explanation):
    print(f"\nCode:\n{code}\n")
    print(f"Explanation:\n{explanation}\n")
   

def main():
    test_codes = [
        """public class SumCalculator {
    public static void main(String[] args) {
        int sum = 0;
        for (int i = 1; i <= 5; i++) {
            sum += i;
        }
        System.out.println("Sum: " + sum);
    }
}""",
        """public class Factorial {
    public static int factorial(int n) {
        if (n == 0 || n == 1) {
            return 1;
        }
        return n * factorial(n - 1);
    }
    
    public static void main(String[] args) {
        int result = factorial(5);
        System.out.println("Factorial: " + result);
    }
}""",
        """public class ArrayMax {
    public static void main(String[] args) {
        int[] numbers = {23, 45, 12, 67, 34};
        int max = numbers[0];
        
        for (int num : numbers) {
            if (num > max) {
                max = num;
            }
        }
        
        System.out.println("Maximum value: " + max);
    }
}""",
        """public class Student {
    private String name;
    private int age;
    
    public Student(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    public void displayInfo() {
        System.out.println("Name: " + name + ", Age: " + age);
    }
    
    public static void main(String[] args) {
        Student student = new Student("Alice", 20);
        student.displayInfo();
    }
}"""
    ]

    for code in test_codes:
       result = explain_code(code)
       format_output(code, result)    


if __name__ == "__main__":
    main()
