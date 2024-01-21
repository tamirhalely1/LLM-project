import os
import subprocess
from openai import OpenAI


client = OpenAI(
    api_key=os.environ.get("OpenAI API Key"),
)

# Define a prompt for generating a Python program
question = "You are an expert python developer. Create for me a python program that checks" \
           " if a number is prime. Do not write any explanations, just show me the code itself." \
           " Also please include unit tests that check the logic of the program using 5 different" \
           " inputs and expected outputs."

# Generate a conversation with OpenAI API to create Python code
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": question,
        }
    ],
    model="gpt-3.5-turbo",
)

# Extract Python code from the OpenAI API response and save it to a file
response = chat_completion.choices[0].message.content
response = response.split("```")
file = open("generatedcode.py", "w")
for i in range(len(response)):
    if response[i][:min(7, len(response[i]))] == "`python":
        code = response[i][8:]
        file.write(code)
file.close()

# Run the generated code using subprocess
subprocess.run(["generatedcode.py"], shell=True, capture_output=True, text=True)




