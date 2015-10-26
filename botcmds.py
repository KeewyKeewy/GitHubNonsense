# botcmds.py


# this is the format of cfg.py, but with generic information
# the real file contains actual login stuff that should never be uploaded
HOST = "irc.twitch.tv"              # the Twitch IRC server
PORT = 6667                         # always use port 6667!
NICK = "xxxxxxxxxxxxxxx"            # your Twitch username, lowercase
PASS = "oauth:xxxxxxxxxxxxxxxxxxxx" # your Twitch OAuth token
CHAN = ["#xxxxxxx",]                # the channel(s) you want to join
ADMINS = ["xxxxx",]                 # Twitch username of global admins
SILENT_AUTO_OFF = ['#xxxxxxxx',]    # channels to automatically turn off silent mode in
# -----------------------------------------------------------------------


RATE = (20/30) # messages per second

# List of links to automatically timeout. Meant to catch bots.
BAN = ['bit.ly', 'goo.gl', '.gu.ma', 'ow.ly', ".3utilities.com", ".gotdns.", ".myftp.", "3cm.ky", "http://t.co", '.myvnc.', 'make.my/', 'bounceme.net', 'youtubee.', '.serveftp.', 'sn.im/'. '/t.co']

# List of phrases to pick up for a joke timeout
FUCKER = ['fuckyoukeewy', 'fuckyou,keewy']

