import os
import subprocess
from openai import OpenAI
import random

client = OpenAI(
    api_key=os.environ.get("OpenAI API Key"),
)

# Define a unit test string to be appended to generated code
unit_test = " Also please include unit tests that check the logic of the program using 5 " \
            "different inputs and expected outputs."

# Define a list of example programs for user selection
PROGRAMS_LIST = [
    '''Given two strings str1 and str2, prints all interleavings of the given 
    two strings. You may assume that all characters in both strings are
    different. Input: str1 = "AB", str2 = "CD"
    Output:
    ABCD
    ACBD
    ACDB
    CABD
    CADB
    CDAB
    Input: str1 = "AB", str2 = "C"
    Output:
    ABC
    ACB
    CAB ''',
    "A program that checks if a number is a palindrome",
    "A program that finds the kth smallest element in a given binary search tree.",
    "A program that implements a data structure which can push, pop and retrieve the minimum element"
    " in O(1) time complexity"
]


# Function to prompt the user for a program selection or choose a random program
def question():
    question_to_ask = input("Tell me, which program would you like me to code for you? If you don't have "
                            "an idea, just press enter and I will choose a random program to code: ")
    if question_to_ask == "":
        random_int = random.randint(0, len(PROGRAMS_LIST) - 1)
        return PROGRAMS_LIST[random_int] + unit_test
    else:
        return question_to_ask + unit_test


# Function to extract and save Python code from the OpenAI API response
def generate_code(response):
    response = response.split("``")
    file = open("generatedcode.py", "w")
    for i in range(len(response)):
        if response[i][:min(7, len(response[i]))] == "`python":
            code = response[i][8:]
            file.write(code)
    file.close()


# Generate a conversation with OpenAI API to create Python code
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": question(),
        }
    ],
    model="gpt-3.5-turbo",
)

# Initialize a counter to limit the number of attempts to generate code
counter = 0

# Attempt to generate and execute code up to 5 times
while counter < 5:
    response = chat_completion.choices[0].message.content

    # Save the generated code to a file
    generate_code(response)

    result = subprocess.run(["python", "generatedcode.py"], capture_output=True, text=True)

    # Check if code execution was successful
    if result.stderr == "":
        print("Code creation completed successfully!")

        # Run the saved code
        subprocess.call("generatedcode.py", shell=True)
        break
    else:
        # Prompt the user to fix errors if code execution fails
        error = "I got these errors, can you fix it? " + result.stderr
        print(f'Error running generated code! Error: {result.stderr}')
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": error,
                }
            ],
            model="gpt-3.5-turbo",
        )
        counter += 1

# Print a message if code generation fails after 5 attempts
if counter == 5:
    print("Code generation FAILED")

