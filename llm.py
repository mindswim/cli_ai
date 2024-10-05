import os
from dotenv import load_dotenv
from openai import OpenAI
import textwrap

# Load environment variables from .env file
load_dotenv()

client = OpenAI()

def get_ai_response(prompt):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a CLI assistant. Provide brief, concise responses similar to command-line help, auto-generated comments, or error messages. Avoid conversational language."},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

def format_cli_output(response):
    lines = response.split('\n')
    formatted_output = []
    
    for line in lines:
        if line.strip().startswith('$'):
            # Command-like output
            formatted_output.append(line.strip())
        else:
            # Comment-like output
            wrapped = textwrap.wrap(line, width=70)
            formatted_output.extend([f"# {l}" for l in wrapped])
        
        formatted_output.append('')  # Add empty line for spacing
    
    return '\n'.join(formatted_output).strip()

def main():
    while True:
        user_input = input("$ ")
        if user_input.lower() == 'exit':
            break
        
        response = get_ai_response(user_input)
        print(format_cli_output(response))
        print()  # Extra newline for readability

if __name__ == "__main__":
    main()

