In this project I implemented 2 different exercises:

1. Developed a program that asks the user for an input to an LLM (Large Language Model)
for a program that the user wants the LLM to code for him. If the user presses
enter, the program will choose a random program to code from a list of options.
afterwards, the program will try to run the code, if succeeded it will stop, else
it will try again while entering to the LLM the error and will try to fix the bugs.
If failed after 5 tries, will print “Code generation FAILED”.

2. Implemented a program that compares between different LLMs' answers.
I have created a list of 50 different questions while giving each question to
wolfram alpha LLM. Those answers were the measure for a good answer for several
different LLMs. Afterwards, I gave two different LLMs the same questions and checked
them according to wolfram alphas' answers. I inserted a unique prompt in order
to get a float number between 0 - 1.0 which simulate the similarity between the answers
into another LLM. When the program finishes to run, it prints to the console the
number of questions answered, the average rating of each LLM and the lowest rating
question and answer of each LLM.
