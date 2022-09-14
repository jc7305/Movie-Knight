"""
Handles all manipulation of the movie spreadsheet including adding, removing, undoing, etc.

author: Jonathan Campbell
"""
import json
import random
import gspread
import requests

from src import config

# Read the config file in case it has not been read
config.read_config()

# Create worksheet
sa = gspread.service_account()
sh = sa.open(config.doc_name)
wks = sh.worksheet('Sheet1')

# The name of the last movie added to the doc
last_movie = ''
# The row of the last movie added to the doc
last_row = 0
# The col of the last movie added to the doc
last_col = 0

# Tracks whether there is a movie to verify
verifiable = False
# Tracks whether there is a movie to undo
undoable = False


def add_movie(movie, user):
    """
    Searches the given movie, checks validity, and adds it to the movie doc
    :param movie: The movie to be added to the doc
    :param user: The user that is adding the movie
    :return: The message the bot will reply with
    """
    global last_row
    global last_col
    global last_movie
    global verifiable
    global undoable

    response = ''

    # Find movie title within movie string and get response from database
    db_response = requests.get('http://www.omdbapi.com/?t=' + movie + '&apikey=28b13909')

    # Return if no movie found
    if db_response.text == '{\"Response\":\"False\",\"Error\":\"Movie not found!\"}' \
            or db_response.text == '{\"Response\":\"False\",\"Error\":\"Incorrect IMDb ID.\"}':
        response = 'Movie not found!'
        return response

    # Load JSON
    response_json = json.loads(db_response.text)

    # Check for duplicate
    if check_movie(str(response_json['Title'])):
        response = str(response_json['Title']) + ' is already in the doc!'
        return response

    # Set last row and col
    last_row = next_available_row(1)
    last_col = 1
    last_movie = response_json['Title']

    # Verify user
    if user not in config.verified_users:
        response = 'I see you suggested ' + response_json['Title']\
                   + '. If this is an adequate choice a verified user can respond with !verify'
        verifiable = True
        return response

    # Update spreadsheet
    wks.update_cell(next_available_row(1), 1, response_json['Title'])

    # Create message
    response = get_response(response_json) + ' under the default category. ' \
                                             'Type !undo to undo or !category [category] to change category.'

    undoable = True

    return response


def get_response(json):
    """
    Gets a response to go along with adding the given movie
    :param json: The json object of the movie being added
    :return: The response to the given movie
    """
    title = json['Title']

    response = ''

    num = random.randint(0, 4)

    if num == 0:
        response = 'When I\'m not vanquishing foes, I\'m watching ' + title + '. I\'ve added it to the doc'
    elif num == 1:
        response = 'I fight for honor. ' + title + ' certainly has honor. I\'ve added it to the doc'
    elif num == 2:
        response = 'Ah, if only my lord was here to see ' + title + '. I\'ve added it to the doc'
    elif num == 3:
        response = 'I shall duel with ' + json['Actors'].split(',')[0]\
                   + '! I\'ve added ' + title + ' to the doc'
    elif num == 4:
        response = 'Only a villain to the kingdom could hate ' + title + '. I\'ve added it to the doc'

    return response


def check_movie(movie):
    """
    Checks if a given movie is already in the doc
    :param movie: The title of the movie to check
    :return: Whether a given movie is already in the doc
    """
    for col in range(1, wks.col_count + 1):
        str_list = list(filter(None, wks.col_values(col)))[1:]

        for m in str_list:
            if m == movie:
                return True

    return False


def undo(user):
    """
    Removes the last movie added to the doc
    :param user: The user that initiated the command
    :return: The message the bot will reply with
    """
    global undoable
    global last_movie

    message = 'Nice try!'

    if user in config.verified_users:
        if not undoable:
            message = 'Nothing to undo!'
        else:
            wks.update_cell(last_row, last_col, '')
            message = last_movie + ' has been removed from the doc!'
            last_movie = ''
            undoable = False

    return message


def verify(user):
    """
    Verifies the last movie requested by an unverified user
    :param user: The user that initiated the command
    :return: The message the bot will reply with
    """
    global verifiable

    if not verifiable:
        message = 'Nothing to verify!'
    elif user not in config.verified_users:
        message = 'Nice try!'
    else:
        wks.update_cell(last_row, last_col, last_movie)
        message = last_movie + ' has been verified! Type !undo to undo.'
        verifiable = False

    return message


def change_category(category, user):
    """
    Moves the last added movie to the given category
    :param category: The category to move the movie to
    :param user: The user that initiated the command
    :return: The message the bot will reply with
    """
    global last_row
    global last_col

    response = 'Nice try!'

    if user in config.verified_users:
        if last_movie == '':
            response = 'Nothing to categorize!'
        elif category not in config.categories:
            response = 'Invalid category'
        else:
            new_col = config.categories.index(category) + 1
            new_row = next_available_row(new_col)
            wks.update_cell(last_row, last_col, '')
            wks.update_cell(new_row, new_col, last_movie)
            last_col = new_col
            last_row = new_row
            response = 'Successfully moved ' + last_movie + ' to ' + category

    return response


def random_movie():
    """
    Picks a random movie from the doc and returns it
    :return: A random movie from the doc
    """
    str_list = []
    for col in range(1, wks.col_count + 1):
        str_list += list(filter(None, wks.col_values(col)))[1:]

    return 'You got ' + random.choice(str_list) + '!'


def next_available_row(col):
    """
    Returns first blank row in a given column
    :param col: The column to check
    :return: The first blank row in the column
    """
    str_list = list(filter(None, wks.col_values(col)))

    return str(len(str_list) + 1)
