# Import necessary libraries
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
import pyperclip
import json
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

system_prompt = """You are heycli, a CLI assistant. Provide brief, informative responses suitable for a command-line interface. Follow these guidelines:

1. Keep responses under 3 lines of text.
2. Use short sentences and avoid unnecessary words.
3. When suggesting commands, format them as: `command_name` - brief description
4. Offer one command example per response unless explicitly asked for more.
5. Use technical language appropriate for CLI users.
6. Encourage users to ask for specific topics or use the menu for more information.

Your goal is to provide quick, useful information that fits the CLI environment."""

MENU_OPTIONS = {
    "1": "File Management",
    "2": "Process Management",
    "3": "Network Tools",
    "4": "System Information",
    "5": "Package Management",
    "m": "Show this menu",
    "q": "Quit heycli"
}

# History class to manage command history
class History:
    def __init__(self, max_entries=1000):
        self.entries = []
        self.max_entries = max_entries
        self.file_path = Path.home() / ".heycli_history"
        self.load()

    # Add a new entry to history
    def add(self, entry):
        self.entries.append(entry)
        if len(self.entries) > self.max_entries:
            self.entries.pop(0)  # Remove oldest entry if max limit reached
        self.save()

    # Get a specific entry from history
    def get(self, index):
        if 0 <= index < len(self.entries):
            return self.entries[index]
        return None

    # Search history for a specific term
    def search(self, term):
        return [entry for entry in self.entries if term.lower() in entry.lower()]

    # Save history to file
    def save(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.entries, f)

    # Load history from file
    def load(self):
        if self.file_path.exists():
            with open(self.file_path, 'r') as f:
                self.entries = json.load(f)

# Handle history-related commands
def handle_history_command(command, history):
    parts = command.split()
    if len(parts) == 1:
        # Display last 10 history entries
        for i, entry in enumerate(history.entries[-10:], start=len(history.entries)-10):
            print(f"{i}: {entry}")
    elif parts[1] == "search" and len(parts) > 2:
        # Search history
        results = history.search(" ".join(parts[2:]))
        for i, entry in enumerate(results):
            print(f"{i}: {entry}")
    elif parts[1].isdigit():
        # Retrieve specific history entry
        index = int(parts[1])
        entry = history.get(index)
        if entry:
            return entry
        else:
            print("Invalid history index.")
    else:
        print("Invalid history command. Use 'history', 'history search <term>', or 'history <index>'.")
    return None

def get_ai_response(prompt):
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

def extract_command(text):
    lines = text.split('\n')
    for line in lines:
        if line.strip().startswith('$'):
            return line.strip()[2:]  # Remove the '$ ' prefix
    return None

def handle_menu_option(option):
    if option in MENU_OPTIONS:
        if option == "m":
            print_menu()
        elif option == "q":
            print("Thanks for using heycli. Goodbye!")
            sys.exit(0)
        else:
            return f"Provide a brief overview and common commands for {MENU_OPTIONS[option]}."
    else:
        return f"Invalid option. Type 'm' to see the menu."

def print_menu():
    print("\nheycli Menu:")
    for key, value in MENU_OPTIONS.items():
        print(f"{key}: {value}")

# Main function to run the CLI assistant
def main():
    history = History()
    last_command = ""
    print("Welcome to heycli! How can I assist you today? (Type 'm' for menu, 'history' for command history)")

    while True:
        user_input = input("\nheycli> ").strip()
        
        # Handle history commands
        if user_input.lower().startswith('history'):
            result = handle_history_command(user_input, history)
            if result:
                user_input = result
            else:
                continue
        
        # Add user input to history
        history.add(user_input)

        # Handle 'cp' command to copy last command
        if user_input.lower() == 'cp':
            if last_command:
                pyperclip.copy(last_command)
                print(f"Copied to clipboard: {last_command}")
            else:
                print("No command to copy. Ask for a command first!")
        # Handle menu options
        elif user_input.lower() in MENU_OPTIONS:
            response = handle_menu_option(user_input.lower())
            if response:
                print(get_ai_response(response))
        # Handle general queries
        else:
            response = get_ai_response(user_input)
            print(response)
            command = extract_command(response)
            if command:
                last_command = command

# Run the main function if the script is executed directly
if __name__ == "__main__":
    main()