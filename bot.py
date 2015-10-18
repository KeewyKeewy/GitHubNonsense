# bot.py

import cfg
import re
import botcmds
# Make sure you prefix the quotes with an 'r'!
CHAT_MSG=re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
import socket
import time
import copy

from urllib.request import urlopen
from json import loads
# network functions go here ________________________________

HOST_CFG = cfg.HOST
PORT_CFG = cfg.PORT
NICK_CFG = cfg.NICK
PASS_CFG = cfg.PASS
CHAN_CFG = cfg.CHAN


# ------------------ Some Definitions ------------------------

BANNED_WORDS = botcmds.BAN
FUCKER_WORDS = botcmds.FUCKER

HOI_LIST = botcmds.HOI

global mods
global chatters

global PET_COUNTER
global TIME_SET

global con
con = socket.socket()

# -------------------- Start Functions -----------------------------

def send_pong(msg):
    con.send(bytes('PONG %s\r\n' % msg, 'UTF-8'))


def send_message(chan, msg):
    con.send(bytes('PRIVMSG %s :%s\r\n' % (chan, msg), 'UTF-8'))


def send_nick(nick):
    con.send(bytes('NICK %s\r\n' % nick, 'UTF-8'))


def send_pass(password):
    con.send(bytes('PASS %s\r\n' % password, 'UTF-8'))


def join_channel(chan):
    con.send(bytes('JOIN %s\r\n' % chan, 'UTF-8'))


def part_channel(chan):
    con.send(bytes('PART %s\r\n' % chan, 'UTF-8'))
    
# ------------------- End Functions ------------------------


# --------------------- Start Helper Functions ------------------------

def get_sender(msg):
    result = ""
    for char in msg:
        if char == "!":
            break
        if char != ":":
            result += char
    return result


def get_message(msg):
    result = ""
    i = 3
    length = len(msg)
    while i < length:
        result += msg[i] + " "
        i += 1
    result = result.lstrip(':')
    return result


def parse_message(sender, msg, channel):
    HOI_CHECK = False
    FUCKER_CHECK = False
    
    BAN_CHECK = True

    CHAN = channel
    
    if len(msg) >= 1:
        ban_check = copy.deepcopy(msg)
        msg = msg.split(' ')
        # a copy of the original message with all the spaces removed
        ban_check = re.sub(' ', '', ban_check)

        for j in BANNED_WORDS:
            if j in ban_check.lower():
                command_timeout(CHAN, sender)
                BAN_CHECK = False

        if BAN_CHECK:
            for i in msg:
                if i.lower() in HOI_LIST:
                    HOI_CHECK = True
                if i.lower() in FUCKER_WORDS:
                    FUCKER_CHECK = True

        if HOI_CHECK or FUCKER_CHECK:
            if FUCKER_CHECK:    
                command_fuckyou(CHAN, sender)
            else:
                command_hoi(CHAN)

        if BAN_CHECK and not FUCKER_CHECK:         
            options = {'!test': command_test,
                       '!pet': command_pet,
                       '!pikmin4': command_pikmin4,
                       '!NERD': command_nerd,
                       '!GetMods': get_mods,
                       '!AmIAMod': check_mod,}
            options_one = {'!timeout': command_timeout, '!fuckyou': command_fuckyou}
     
            if msg[0] in options:
                if msg[0] == '!AmIAMod' or msg[0] == '!GetMods':
                    options[msg[0]](CHAN, sender)
                else:   
                    options[msg[0]](CHAN)
            elif msg[0] in options_one:
                try:
                    options[msg[0]](CHAN, msg[1])
                except KeyError:
                    # Key is not present
                    send_message(CHAN, 'One parameter is required.')
                    pass


# -------------- End Helper Functions -------------------


# -------------------- Start Command Functions -----------------

def command_test(CHAN):
    """A command to test if the bot is working.

string > msg"""
    send_message(CHAN, "Hope I'm not broken.")

def command_hoi(CHAN):
    """hOI!

string > msg"""
    send_message(CHAN, "hOI!")


def command_pikmin4(CHAN):
    """A command to express the hype that is Pikmin 4.

string > msg"""
    send_message(CHAN, "PIKMIN 4 CoolCat")

def command_nerd(CHAN):
    """A command to poke fun at the nerds in chat.

string > msg"""
    send_message(CHAN, "FrankerZ ")
    send_message(CHAN, "FrankerZ FrankerZ ")
    send_message(CHAN, "FrankerZ FrankerZ FrankerZ ")
    send_message(CHAN, "FrankerZ FrankerZ ")
    send_message(CHAN, "FrankerZ ")
    send_message(CHAN, "GET FUCKO'D")


def command_pet(CHAN):
    send_message(CHAN, 'Lesser Dog got excited.')

def get_mods(CHAN, username):
    response = urlopen('https://tmi.twitch.tv/group/user/' + CHAN[1:] + '/chatters')
    readable = response.read().decode('utf-8')
    chatlist = loads(readable)
    #load the moderator list
    mods = chatters['moderators']
    print ("Reloaded the Modlist")
    
def check_mod(CHAN, username):
    print(username)
    if username in mods:
        send_message(CHAN, "Yes")
    else:
        send_message(CHAN, "No, " + username + " , you aren't")
    
# The full petting command is long.

##def command_pet(CHAN):
##    global PET_COUNTER
##    if PET_COUNTER < 3:
##        send_message(CHAN, 'KeewyDog')
##        send_message(CHAN, 'Lesser Dog got excited.')
##        PET_COUNTER = PET_COUNTER + 1
##        TIME_SET = time.time()
##        
##    elif PET_COUNTER > 2 and PET_COUNTER < 6:
##        send_message(CHAN, 'KeewyDog')
##        send_message(CHAN, 'KeewyLesser')
##        send_message(CHAN, "It's already overexcited.")
##        PET_COUNTER = PET_COUNTER + 1
##        
##    elif PET_COUNTER > 5 and PET_COUNTER < 9:
##        send_message(CHAN, 'KeewyDog')
##        send_message(CHAN, 'KeewyLesser')
##        send_message(CHAN, 'KeewyLesser')
##        send_message(CHAN, "Lesser Dog is overstimulated.")
##        PET_COUNTER = PET_COUNTER + 1
##        
##    elif PET_COUNTER > 8 and PET_COUNTER < 12:
##        send_message(CHAN, 'KeewyLesser')
##        send_message(CHAN, 'KeewyLesser')
##        send_message(CHAN, 'KeewyLesser')
##        send_message(CHAN, "Lesser Dog shows no sign of stopping.")
##        PET_COUNTER = PET_COUNTER + 1
##
##    elif PET_COUNTER > 11 and PET_COUNTER < 15:
##        send_message(CHAN, 'KeewyLesser KeewygoD')
##        send_message(CHAN, 'KeewyLesser')
##        send_message(CHAN, 'KeewyLesser')
##        send_message(CHAN, "You can reach Lesser Dog again.")
##        PET_COUNTER = PET_COUNTER + 1
##
##    elif PET_COUNTER > 14 and PET_COUNTER < 18:
##        send_message(CHAN, 'KeewyLesser KeewyLesser')
##        send_message(CHAN, 'KeewyLesser KeewygoD')
##        send_message(CHAN, 'KeewyLesser')
##        send_message(CHAN, "It's possible that you may have a problem.")
##        PET_COUNTER = PET_COUNTER + 1
##        
##    elif PET_COUNTER > 17 and PET_COUNTER < 21:
##        send_message(CHAN, 'KeewyLesser KeewyLesser')
##        send_message(CHAN, 'KeewyLesser KeewyLesser')
##        send_message(CHAN, 'KeewyLesser KeewygoD')
##        send_message(CHAN, "Lesser Dog is unpettable but appreciates the attempt.")
##        PET_COUNTER = PET_COUNTER + 1
##
##    elif PET_COUNTER > 20 and PET_COUNTER < 23:
##        send_message(CHAN, 'KeewyLesser KeewyLesser')
##        send_message(CHAN, 'KeewyLesser KeewyLesser')
##        send_message(CHAN, 'KeewyLesser KeewyLesser')
##        send_message(CHAN, "Lesser Dog has gone where no dog has gone before.")
##        PET_COUNTER = PET_COUNTER + 1
##
##    elif PET_COUNTER > 22:
##        send_message(CHAN, "Really...")
##        PET_COUNTER = PET_COUNTER + 1

# End of Lesser Dog shenanigans.        

def command_timeout(CHAN, name):
    """Uses the /timeout command to timeout a user.

str, str > msg"""
    send_message(CHAN, '/timeout ' + name + ' 60')
    send_message(CHAN, name + ' timed out because of shortened link.')
    
def command_fuckyou(CHAN, name):
    """Uses the /timeout command cause lol fuck you too.

str, str > msg"""
    send_message(CHAN, '/timeout ' + name + ' 5')
    send_message(CHAN, name + ' timed out because lol fuck you too.')


    
# ------------- End Command Functions -----------------

# --------- Function for Starting Bot While Loop ---------

def start_bot(HOST, PORT, PASS, NICK, CHAN):
    """Takes the cfg.py settings and starts the while loop that runs the bot.

str, str, str, str, str -> none"""

    con.connect((HOST, PORT))

    send_pass(PASS)
    send_nick(NICK)
    join_channel(CHAN)

    data = ""

    PET_COUNTER = 0
    TIME_SET = time.time()

    while True:
        try:
                    
            data = data+con.recv(1024).decode('UTF-8')
            data_split = re.split(r"[~\r\n]+", data)
            data = data_split.pop()

            for line in data_split:
                line = str.rstrip(line)
                line = str.split(line)

                if len(line) >= 1:
                    #This runs once the bot has recieved confimation it's joined
                    if line[1] == 'JOIN':
                        response = urlopen('https://tmi.twitch.tv/group/user/' + CHAN[1:] + '/chatters')
                        readable = response.read().decode('utf-8')
                        chatlist = loads(readable)
                        #load the current people in chat
                        chatters = chatlist['chatters']
                        #load the moderator list
                        mods = chatters['moderators']
                        print ("Joined and loaded")

                    if line[0] == 'PING':
                        send_pong(line[1])

                    if line[1] == 'PRIVMSG':
                        sender = get_sender(line[0])
                        message = get_message(line)
                        parse_message(sender, message, CHAN)

                        print(sender + ": " + message)

            if (TIME_SET - time.time()) < -120 or (TIME_SET - time.time())> 0:
                PET_COUNTER = 0
                print(PET_COUNTER)
                TIME_SET = time.time()
            
            time.sleep(1 / botcmds.RATE)

        except socket.error:
            print("Socket died")

        except socket.timeout:
            print("Socket timeout")


# ---------- End Bot Function -----------

start_bot(HOST_CFG, PORT_CFG, PASS_CFG, NICK_CFG, CHAN_CFG)
