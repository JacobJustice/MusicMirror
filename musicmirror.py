#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
Telegram bot to add spotify tracks to a collaborative playlist requires telegram bot and spotify api credentials.

Press Ctrl-C on the command line or send a signal to the process to stop the bot.
"""

import logging
import sys
import json
import time

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import MessageEntity

import spotipy
import spotipy as util

# Enable logging
logging.basicConfig(
    format='%(levelname)s:%(asctime)s - %(name)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('mm.log'),
        logging.StreamHandler(sys.stdout)
    ]

)

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text("""Send a link to a spotify track and I will find the artist, track name, and the album art.
        \nI will also add the track to this spotify playlist: https://open.spotify.com/playlist/"""+playlist_id)


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text("""Send a link to a spotify track and I will find the artist, track name, and the album art.
            \nI will also add the track to this spotify playlist: https://open.spotify.com/playlist/"""+playlist_id)


# if the substring isn't found, return length of string
def find_wrap(string, substring):
    find_val = string.find(substring)
    if find_val < 0:
        return len(string)
    else:
        return find_val 


def extract_track_id(text):
    url_ind = text.find("https://open.spotify.com/track/")

    # cut everything before the url
    track_url = text[url_ind:]

    # cut everything after the track_url if there is anything after the track_url
    if track_url.find(' ') != -1:
        track_url = track_url[:track_url.find(' ')]

    # cut everything before /track/ and after the ? (inclusive)
    track_id = track_url[track_url.find('/track/')+len('/track/'):find_wrap(track_url,'?')]

    print(track_url)
    print(track_id)

    return track_id, '?' in track_url


def generate_reply(track_dict):
    image_url = track_dict['album']['images'][0]['url']
    artist_names = ''
    for i, artist in enumerate(track_dict['album']['artists']):
        if i == 0:
            artist_names += artist['name']
        else:
            artist_names += ', ' + artist['name']
    track_name = track_dict['name']
    reply = artist_names + " - " + track_name
    return reply, image_url


def reply_with_track_info(update: Update, context: CallbackContext) -> None:
    if contains_spotify_link(update.message.text):
        spot_token = util.prompt_for_user_token(username,
                                           scope,
                                           client_id=spotify_cred['id'],
                                           client_secret=spotify_cred['secret'],
                                           redirect_uri=spotify_cred['redirect'])
        sp = spotipy.Spotify(auth=spot_token)

        track_id, long_link = extract_track_id(update.message.text)
        track_dict = sp.track(track_id)
        reply, image_url = generate_reply(track_dict)
        if update.message.from_user.username != None:
            logging.info(str(update.message.from_user.id) + ':' + update.message.from_user.username + '; ' + reply + ', ' + image_url)
        else:
            logging.info(str(update.message.from_user.id) + ';' + reply + ', ' + image_url)

        reply += '\n\n' + image_url

        if long_link:
            update.message.reply_text(reply)

        # remove all occurences of the track
        sp.user_playlist_remove_all_occurrences_of_tracks(username, playlist_id,[track_id])
        # add the track
        results = sp.user_playlist_add_tracks(username, playlist_id, [track_id],position=0)


def contains_spotify_link(text):
    return "https://open.spotify.com/track/" in text


"""Start the bot."""
# Load telegram bot token
with open('/home/andrew/MusicMirror/telegram_token.json') as f_t:
    tel_token = json.load(f_t)['token']

# Load spotify credentials
spotify_cred = None
with open('/home/andrew/MusicMirror/spotify.json') as f_s:
    spotify_cred = json.load(f_s)
username = spotify_cred['username']
playlist_id = spotify_cred['playlist']

scope = 'playlist-modify-public playlist-modify-private'
#spot_token = util.prompt_for_user_token(username,
#                                   scope,
#                                   client_id=spotify_cred['id'],
#                                   client_secret=spotify_cred['secret'],
#                                   redirect_uri=spotify_cred['redirect'])
#
#if spot_token:
#    print('TOKEN',spot_token)
#    sp = spotipy.Spotify(auth=spot_token)
#else:
#    print("Couldn't get token for",username)
#    sys.exit()

# Create the Updater and pass it your bot's token.
updater = Updater(tel_token)

# Get the dispatcher to register handlers
dispatcher = updater.dispatcher

# on different commands - answer in Telegram
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_command))

# on non command i.e message - echo the message on Telegram
dispatcher.add_handler(MessageHandler(Filters.entity('url') & ~Filters.command, reply_with_track_info))

# Start the Bot
updater.start_polling()

print("\n\n\t\tMusicMirror Started!\n\n")

# Run the bot until you press Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT. This should be used most of the time, since
# start_polling() is non-blocking and will stop the bot gracefully.
updater.idle()
