"""
Handles reading configuration files

author: Jonathan Campbell
"""

# The token for the discord bot
bot_token = ''
# The id of the discord bot
bot_id = ''
# The name of the Google spreadsheet
doc_name = ''
# The organization name of the openai account
openai_organization = ''
# The api key of the openai account
openai_api_key = ''
# The list of all users verified to add movies to the doc
verified_users = []
# The list of categories
categories = []


def read_config():
    """
    Reads the config file and sets the appropriate variables
    """
    global bot_token
    global bot_id
    global doc_name
    global openai_organization
    global openai_api_key

    f = open('config.txt', 'r')

    bot_token = f.readline().split(': ')[1][:-1]
    bot_id = f.readline().split(': ')[1][:-1]
    doc_name = f.readline().split(': ')[1][:-1]
    openai_organization = f.readline().split(': ')[1][:-1]
    openai_api_key = f.readline().split(': ')[1]

    read_verified()
    read_categories()

    f.close()


def read_verified():
    """
    Reads the verified file and puts users in verified_users
    """
    f = open('verified.txt', 'r')

    for line in f:
        verified_users.append(line.replace('\n', ''))

    f.close()


def read_categories():
    """
    Reads the categories file and puts categories in categories
    """
    f = open('categories.txt', 'r')

    for line in f:
        categories.append(line.replace('\n', ''))

    f.close()
