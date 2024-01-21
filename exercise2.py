from gpt4all import GPT4All
import requests
import numpy as np
import time
import re
import redis
from datetime import timedelta


def wolfram_alpha_response(question):
    # Set Wolfram Alpha app ID
    app_id = "3LJXKW-JGUJHYTUP2"

    # Split the input question into a list of words
    question_list = question.split()

    # Create a string by joining the words with '+' for URL encoding
    question_string = ""
    for i in range(len(question_list) - 1):
        question_string += question_list[i] + "+"
    question_string += question_list[-1]

    # Construct the Wolfram Alpha API URL with the question and app ID
    url = f'https://api.wolframalpha.com/v1/result?i={question_string}%3F&appid={app_id}'

    # Send a GET request to the Wolfram Alpha API
    response = requests.get(url)

    # Decode the response content from UTF-8
    response = response.content.decode("utf-8")
    return response


def model_response(model_name, question):
    # Check the model name to determine the appropriate format for the input question
    if model_name == "mistral-7b-instruct-v0.1.Q4_0.gguf":
        model_question = "[INST]" + question + "[/INST]"
    elif model_name == "mistral-7b-openorca.Q4_0.gguf" or model_name == "orca-2-7b.Q4_0.gguf":
        model_question = "### Human: " + "\n" + question + "\n" + "### Assistant: "

    # Initialize the GPT-4 model with the specified model name
    model = GPT4All(model_name)

    # Generate a response using the model and the formatted question
    output = model.generate(model_question, max_tokens=300)
    return output


def read_csv(file_name):
    # Read the CSV file into a NumPy array using ',' as the delimiter and strings as the data type
    question_array = np.genfromtxt(file_name, delimiter=",", dtype=str)

    # Extract categories and questions from the array
    categories = question_array[1:, 0]
    questions = question_array[1:, 1]

    # Convert categories and questions to Python lists and return them
    return categories.tolist(), questions.tolist()


def extract_num(local_llm_answer):
    # Use regular expression to find the first floating-point or integer number in the input string
    match = re.search(r'\b\d+\.\d+\b', local_llm_answer)

    # Extract the matched number as a string
    float_number_str = match.group() if match else None

    # Convert the string to a float if it contains a decimal point, otherwise convert to an integer
    if float_number_str:
        float_number = float(float_number_str) if '.' in float_number_str else int(float_number_str)
        return float_number
    return None


def data_calculation(data_list):
    # Initialize variables for calculating statistics for mistral-7b-openorca.Q4_0.gguf
    sum_of_rating_llm1 = 0
    lowest_rating_llm1 = 1
    index_lowest_llm1 = 0

    # Initialize variables for calculating statistics for orca-2-7b.Q4_0.gguf
    sum_of_rating_llm2 = 0
    lowest_rating_llm2 = 1
    index_lowest_llm2 = 0

    # Iterate through the data_list to calculate sum and find the lowest rating for each model
    for i in range(len(data_list)):
        if data_list[i][-1]:
            if data_list[i][1] == "mistral-7b-openorca.Q4_0.gguf":
                sum_of_rating_llm1 += data_list[i][-1]
                if data_list[i][-1] < lowest_rating_llm1:
                    lowest_rating_llm1 = data_list[i][-1]
                    index_lowest_llm1 = i
            if data_list[i][1] == "orca-2-7b.Q4_0.gguf":
                sum_of_rating_llm2 += data_list[i][-1]
                if data_list[i][-1] < lowest_rating_llm2:
                    lowest_rating_llm2 = data_list[i][-1]
                    index_lowest_llm2 = i

    # Calculate average ratings for each model
    average_rating_llm1 = 2 * (sum_of_rating_llm1 / len(data_list))
    average_rating_llm2 = 2 * (sum_of_rating_llm2 / len(data_list))
    return average_rating_llm1, average_rating_llm2, index_lowest_llm1, index_lowest_llm2


local_LLM = "mistral-7b-instruct-v0.1.Q4_0.gguf"
llm_models = ["mistral-7b-openorca.Q4_0.gguf", "orca-2-7b.Q4_0.gguf"]
llm_models_name = ["Mistral OpenOrca", "Orca 2(Medium)"]
file_name = "./General_Knowledge_Questions.csv"

# Initialize Redis connection
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Read categories and questions from the CSV file
categories, questions = read_csv(file_name)

# Obtain Wolfram Alpha answers for each question
wolfram_alpha_answers = []
for question in questions:
    cached_response = redis_client.get(question)

    if cached_response:
        # If cached response exists, return it
        wolfram_alpha_answers.append(cached_response.decode("utf-8"))
    else:
        response = wolfram_alpha_response(question)
        wolfram_alpha_answers.append(response)
        redis_client.setex(question, timedelta(hours=4), response)

# Initialize an empty list to store model performance statistics
model_performance = []

# Initialize a variable to count the number of questions answered
number_of_questions_answered = 0

for i in range(len(questions)):
    # Check if Wolfram Alpha did not understand the input, and skip to the next iteration if true
    if wolfram_alpha_answers[i] == "Wolfram|Alpha did not understand your input":
        continue

    # Increment the number of questions answered
    number_of_questions_answered += 1

    # Iterate through the additional language models to compare their responses
    for j in range(len(llm_models)):
        # Extract question and model name for the current iteration
        question = questions[i]
        model_name = llm_models[j]

        # Measure the time taken for the model to respond
        start = time.time()
        model_answer = model_response(model_name, question)
        end = time.time()
        model_run_time = 1000 * (end - start)

        # Generate a local language model question for comparison
        local_LLM_question = f'I am going to give you a question which I do not want you to answer: {question}' \
                             f' Here are two optional answers from two different LLM models:' \
                             f'The first one: {wolfram_alpha_answers[i]} and the second one: {model_answer}' \
                             f' Please rate how similar the two answers on a scale of 0 - 1.0.'

        # Obtain a response from the local language model and extract correctness rating
        local_model_response = model_response(local_LLM, local_LLM_question)
        correctness = extract_num(local_model_response)

        # Store the data for the current question and model in model_performance list
        current_data = [question, model_name, model_answer, model_run_time, correctness]
        model_performance.append(current_data)

# Calculate and print performance statistics for the language models
avg_rating_llm1, avg_rating_llm2, index_low_llm1, index_low_llm2 = data_calculation(model_performance)
print(f'Number of questions answered: {number_of_questions_answered} \n'
      f'Average answer rating of {llm_models_name[0]}: {avg_rating_llm1} \n'
      f'Average answer rating of {llm_models_name[1]}: {avg_rating_llm2} \n'
      f'Lowest rating question and answer of {llm_models_name[0]}: {model_performance[index_low_llm1][0]} {model_performance[index_low_llm1][2]} \n'
      f'Lowest rating question and answer of {llm_models_name[1]}: {model_performance[index_low_llm2][0]} {model_performance[index_low_llm2][2]}')








