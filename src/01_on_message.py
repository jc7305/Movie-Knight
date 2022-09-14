"""
Handles general bot functions and includes a method to process received messages

author: Jonathan Campbell
"""
import discord
import movie_doc

from src import ai, config

# The discord client used to get messages, users, and channels
client = discord.Client()


@client.event
async def on_message(message):
    """
    Called whenever a discord message is sent and processes the message
    :param message: The discord message
    """
    content = message.content.lower()
    author = str(message.author)

    # Returns if message is from bot
    if message.author == client.user:
        return

    # AI Response if bot is pinged
    if '<@' + str(config.bot_id) + '>' in content:
        await message.channel.send(ai.get_response(str(message.content).replace('<@' + str(config.bot_id) + '>', ''),
                                                   author[:-5]))
        return

    # Undo command
    if content == '!undo':
        await message.channel.send(movie_doc.undo(author))

    # Verify command
    if content == '!verify':
        await message.channel.send(movie_doc.verify(author))

    # Category command
    if content[0:9] == '!category':
        await message.channel.send(movie_doc.change_category(content[10:], author))

    # Random command
    if content == '!random':
        await message.channel.send(movie_doc.random_movie())

    # Add movie command
    if content[0:4] == '!add':
        await message.channel.send(movie_doc.add_movie(content[5:], author))


client.run(config.bot_token)
