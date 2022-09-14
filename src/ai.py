"""
Handles all AI requests such as getting custom message responses

author: Jonathan Campbell
"""
import re
import openai

from src import config

# Read the config file in case it has not been read
config.read_config()

# Configure openai
openai.organization = config.openai_organization
openai.api_key = config.openai_api_key
openai.Model.list()

# Open prompt file
f = open('prompt.txt', 'r')
prompt = (f.read())


def get_response(message, name):
    global prompt

    # Cut message to manageable size and remove new lines
    if len(message) > 115:
        message = message[:115]
    if '\n' in message:
        message = message[:message.rfind('\n')]

    # Generate response
    response = openai.Completion.create(
      model="text-curie-001",
      prompt=prompt + name + ': ' + message + '\nMovie Knight:',
      max_tokens=25,
      temperature=0.8
    )

    # Extract text from response object
    response = response.to_dict()['choices'][0].to_dict()['text']

    # Find punctuation
    period = response.rfind('.')
    exclamation = response.rfind('!')
    question = response.rfind('?')
    comma = response.rfind(',')

    # Cut response at punctuation if possible
    cut = response
    if period != -1 or exclamation != -1 or question != -1 or comma != -1:
        cut = response[:max(period, exclamation, question, comma - 1) + 1]

    # Try again if empty response or tries to respond for another person
    if re.search('[^\n ]', cut) is None or ':' in cut:
        return get_response(message, name)

    # Update prompt
    prompt += name + ': ' + message + '\nMovie Knight: ' + cut + '\n'
    file = open("prompt.txt", "r")
    if prompt.count("\n") > 5:
        prompt = file.read() + "\n".join(prompt.split("\n")[len(prompt.split("\n")) - 5:])
    file.close()

    return cut
