# bot.py

import cfg, re, settings, botcmds, socket, time, copy, random
from multiprocessing import Process

# Make sure you prefix the quotes with an 'r'!
CHAT_MSG=re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")


from urllib.request import urlopen
from json import loads, load, dump


# network functions go here ________________________________

HOST_CFG = cfg.HOST
PORT_CFG = cfg.PORT
NICK_CFG = cfg.NICK
PASS_CFG = cfg.PASS
CHAN_CFG = cfg.CHAN


# ------------------ Some Definitions ------------------------

BANNED_WORDS = settings.BAN
FUCKER_WORDS = settings.FUCKER


global mods
global chatters

global admins
admins = cfg.ADMINS

global SILENT_MODE

global con
con = socket.socket()

global negwords

with open("negative.json", "r") as neg:
    negwords = load(neg)

# ------------------ Start State Classes ------------------------

class StateMachine(object):
    """Handles state transition info as well as what state this instance of the bot has.
        Each instance of a bot should have one. May want to put any and all bot info in this later"""
    def __init__(self):
        self.transitions = {
            "!normal":NormalState,
            "!silent":SilentState,
            "!modsonly":ModState,
            "!game":GameState,
        }
        self.currentState = NormalState()

    def get_state():
        return self.currentState

    def get_state_name():
        if self.currentState == NormalState:
            return "normal"
        elif self.currentState == SilentState:
            return "silent"
        elif self.currentState == ModState:
            return "modsonly"
        elif self.currentState == GameState:
            return "game"

class NormalState(object):
    """Contains silly commands for all viewers, and some mod only commands"""
    def __init__(self):
        self.commands = {
            '!test': command_test,
            '!pikmin4': command_pikmin4,
            '!getmods': get_mods,
            '!amiamod': command_am_i_a_mod,
            '!pet': command_pet,
            '!nerd': command_nerd,
            'hoi': command_hoi,
            'hoi!': command_hoi,
            '!rimshot':command_rimshot,
            '!sagewisdom' : command_sage_wisdom,
            '!quote' : command_quote,
            'dear' : command_ask_tem,
            'you' : command_know_what_else,}
        # put in banables and fucker words because they're technically commands
        self.modCommands = {'!togglepet': command_pet_toggle,
            '!pettoggle': command_pet_toggle,
            "!silent": change_state,
            "!modsonly": change_state,
            "!game": change_state,
            "!writequote" : command_write_quote,
            "!leave": command_leave,}

class SilentState(object):
    """the bot says nothing but still continues banning work"""
    def __init__(self):
        self.commands = {}
        # put in banables and fucker words because they're technically commands
        self.modCommands = {
            "!normal": change_state,
            "!modsonly": change_state,
            "!game": change_state,
            "!leave": command_leave,}

class ModState(object):
    """Only mods have access to all commands the bot can do"""
    def __init__(self):
        self.commands = {}
        # put in banables and fucker words because they're technically commands
        self.modCommands = {
            'hoi': command_hoi,
            'hoi!': command_hoi,
            '!togglepet': command_pet_toggle,
            '!pettoggle': command_pet_toggle,
            '!test': command_test,
            '!pikmin4': command_pikmin4,
            '!getmods': get_mods,
            '!amiamod': command_am_i_a_mod,
            '!pet': command_pet,
            '!nerd': command_nerd,
            "!normal": change_state,
            "!silent": change_state,
            "!modsonly": change_state,
            "!game": change_state,
            '!rimshot': command_rimshot,
            '!sagewisdom' : command_sage_wisdom,
            '!quote' : command_quote,
            '!writequote' : command_write_quote,
            "!leave": command_leave,
            'you' : command_know_what_else,}

class GameState(object):
    """Only commands relevant to the game or banable actions are active"""
    def __init__(self):
        self.commands = {}
        # put in banables and fucker words because they're technically commands
        self.modCommands = {
            "!normal": change_state,
            "!silent": change_state,
            "!modsonly": change_state,
            "!leave": command_leave,}
        

def change_state(statemachine, newstate):
    statemachine.currentState = newstate()


# --------------------- Message Class ------------------------------
class MessageObject(object):
    """contains all relevant information to the message in one place"""
    def __init__ (self, msgChan, sender, msg):
        self.channel = msgChan
        self.sender = sender
        self.message = msg

    def get_channel(self):
        return self.channel

    def get_sender(self):
        return self.sender

    def get_message(self):
        return self.message

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


def parse_message(sender, msg, channel, mybotstate):
    # --- Varialbe Definitions ---
    #global SILENT_MODE
    
    FUCKER_CHECK = False
    BAN_CHECK = True

    CHAN = channel

    # --- End Definitions ---
    
    if len(msg) >= 1:
        msg_object = MessageObject(channel, sender, copy.deepcopy(msg))
        ban_msg = copy.deepcopy(msg)
        msg = msg.split(' ')
        # a copy of the original message with all the spaces removed
        ban_msg = re.sub(' ', '', ban_msg)

        for j in BANNED_WORDS:
            if j in ban_msg.lower():
                command_timeout(msg_object)
                BAN_CHECK = False

        if BAN_CHECK:
            for i in FUCKER_WORDS:
                if i in ban_msg.lower():
                    command_fuckyou(msg_object)
                    FUCKER_CHECK = True

        #now we check each part of the state machine
        for i in msg:
            if i.lower() in mybotstate.currentState.commands:
                mybotstate.currentState.commands[i.lower()](msg_object)
                #TODO: will need to update this to support commands with parameters
            elif i.lower() in mybotstate.currentState.modCommands and check_mod(msg_object):
                if i.lower() in mybotstate.transitions:
                    #transition to next
                    change_state(mybotstate, mybotstate.transitions[i.lower()])
                    send_message(CHAN, "Keewybot is now in " + i.lower()[1:] + " mode.")
                else:
                    mybotstate.currentState.modCommands[i.lower()](msg_object)


# -------------- End Helper Functions -------------------


# -------------------- Start Command Functions -----------------
# ALL COMMANDS REQUIRE CHAN AND SENDER, EVEN IF THEY DON'T USE IT
def command_test(msg_object):
    """A command to test if the bot is working.

str > none"""
    send_message(msg_object.get_channel(), "Hope I'm not broken.")

def command_hoi(msg_object):
    """hOI!

str > none"""
    global TEM_CHECK
    global TIMER_TEMMIE
    if TEM_CHECK:
        send_message(msg_object.get_channel(), "hOI ! ! !")
        TIMER_TEMMIE = time.time()
        TEM_CHECK = False


def command_pikmin4(msg_object):
    """A command to express the hype that is Pikmin 4.

str > none"""
    send_message(msg_object.get_channel(), "PIKMIN 4 CoolCat")

def command_know_what_else(msg_object):
    neg_check = False
    not_check = False
    global negwords
    not_words = ["not", "isn't", "isnt", "doesn't", "doesnt",]
    msg_check = msg_object.message.lower().replace('?', "").split(' ')
    if "know" in msg_object.message.lower() and "what" in msg_object.message.lower() and "else" in msg_object.message.lower():
        for word in msg_check:
            if word in negwords:
                neg_check = True
                pass
        for word in msg_check:
            if word in not_words:
                if not_check == False:
                    not_check = True
                else:
                    not_check = False
        if not_check:
            if neg_check == False:
                neg_check = True
            else:
                neg_check = False
        if neg_check:
            neg_response = ["PIKM. . . hey wait a second.",
                            "I don't know.",
                            "Good question.",
                            msg_object.get_sender(),]
            send_message(msg_object.get_channel(), random.choice(neg_response))
        else:
            send_message(msg_object.get_channel(), "PIKMIN 4 CoolCat")

def command_nerd(msg_object):
    """A command to poke fun at the nerds in chat.

string > none"""
    if msg_object.get_sender() in mods or msg_object.get_sender() in admins:
        send_message(msg_object.get_channel(), "KeewyDog ")
        send_message(msg_object.get_channel(), "KeewyLesser KeewyDog ")
        send_message(msg_object.get_channel(), "KeewyLesser KeewyLesser KeewyDog ")
        send_message(msg_object.get_channel(), "KeewyLesser KeewyDog ")
        send_message(msg_object.get_channel(), "KeewygoD ")
        send_message(msg_object.get_channel(), "FUCKO'D")
    else:
        send_message(msg_object.get_channel(), '/timeout ' + msg_object.get_sender() + ' 1')
        send_message(msg_object.get_channel(), msg_object.get_sender() + ' is a nerd.')
    
def get_mods(msg_object):
    global mods
    global chatters
    response = urlopen('https://tmi.twitch.tv/group/user/' + msg_object.get_channel()[1:] + '/chatters')
    readable = response.read().decode('utf-8')
    chatlist = loads(readable)
    #load the moderator list
    chatters = chatlist['chatters']
    mods = chatters['moderators']
    print ("Reloaded the Modlist")
    
def check_mod(msg_object):
    global mods
    global chatters
    global admins
    if msg_object.get_sender() in mods or msg_object.get_sender() in admins:
        return True
    else:
        return False

def command_am_i_a_mod(msg_object):
    global mods
    global chatters
    global admins
    if msg_object.get_sender() in mods or msg_object.get_sender() in admins:
        send_message(msg_object.get_channel(), "Yes, " + msg_object.get_sender() + ", obviously")
    else:
        send_message(msg_object.get_channel(), "No, " + msg_object.get_sender() + ", you aren't")

def command_timeout(msg_object):
    """Uses the /timeout command to timeout a user.

str, str > msg"""
    send_message(msg_object.get_channel(), '/timeout ' + msg_object.get_sender() + ' 60')
    send_message(msg_object.get_channel(), msg_object.get_sender() + ' timed out because of bot-related link.')
    
def command_fuckyou(msg_object):
    """Uses the /timeout command cause lol fuck you too.

str, str > msg"""
    send_message(msg_object.get_channel(), '/timeout ' + msg_object.get_sender() + ' 1')
    send_message(msg_object.get_channel(), msg_object.get_sender() + ' timed out because lol fuck you too.')

def command_rimshot(msg_object):
    if random.random() > 0.9:
        send_message(msg_object.get_channel(), "that wasn't actually that funny")
    else:
        send_message(msg_object.get_channel(), "*BA DUM TSSH*")

def command_sage_wisdom(msg_object):
    baseadvice = ["Pigs are smarter than bears but they can't ride motorcycles.",
        "Have you tried turning it off and then back on again?",
        "Do the thing with the thing",
        "Press the win button",
        "The winner is the one who sucks the least. But let me be clear: you still suck.",
        "As a great monarch once stated: :U",
        "Naw, not feeling like wisdom right now",
        "Are fish tacos shaped liked a fish?",
        "Lift your keyboard directly above your head, then slightly tilt and flip it",
        "Never put your hand where you wouldn't put your willy",
        "Try recoloring your stream layout into BRIGHT NEON COLORS",
        "Tell C to come up with 5 more puns about it and beat it to death",
        "Try not to bonk into things 3 times in a row",
        "Rub some bacon on it",
        "Nothing I can say will help at this point",
        "Remember to change your stream title",
        "No reason to worry, you won't get world record anyways",
        "I found this trick as a kid. It's not that hard, you can do it",
        "There are plenty of ways to mess up, but you don't need to find all of them",
        "We don't make mistakes, just happy little accidents",]
    channeladvice = {"#sirtet":["Don't forget Gelato 7",
                                "Pick up blue coins to regain two health points. These are rare coins that may interest a certain shopkeeper",
                                "Don't take ages on this skip",
                                "Choose a file block containing saved game data, then select Score from the menu. Choosing Score allows you to check the number of fucks I give",                           
                                ],
                     "#c7_the_epic":["I'd say don't suck, but you obviously need to suck more",
                                   "Don't run around people's mansions humping chests",
                                   "Large Pearls are acquired by sucking up a portrait ghost in one go.  They are worth 1 million dollars and are essential to Luigi's Mansion 100% runs",
                                   "Water your fruits and vegetables. Also, the plant.",
                                   "Calm down; It's only the bonus room Kappa ",
                                   ]}
    if msg_object.get_channel() in channeladvice:
        advice = baseadvice + channeladvice[msg_object.get_channel()]
    else:
        advice = baseadvice
    send_message(msg_object.get_channel(), random.choice(advice))

def command_ask_tem(msg_object):
    """
"""
    global TEM_CHECK
    global TIMER_TEMMIE
    msg = msg_object.get_message()
    msg_check = msg.replace("dear", "")
    msg_check = msg_check.split(' ')
    response = ["* tem... have a solushun! temMIE",
                "* OMG!! humans TOO CUTE (dies) temMIE",
                "* go to TEM SHOP!!! temMIE",
                "* WOA!!! temMuns",
                "* hnn, tem think... temMIE",
                "* go to colleg! temMIE",
                "* don forget my friend! temMIE",]
    # add in "You will regret this." when there are more options.
    if TEM_CHECK:
        if "dear tem" in msg.lower():
            if "tem flake" in msg.lower() or "temmie flake" in msg.lower():
                TIMER_TEMMIE = time.time()
                TEM_CHECK = False
                send_message(msg_object.get_channel(), "* TEM LOVE TEM FLAKE temMuns")
            elif "history" in msg.lower():
                TIMER_TEMMIE = time.time()
                TEM_CHECK = False
                send_message(msg_object.get_channel(), msg_object.get_sender() + ", " + "* us tems have a deep history!!! temMIE")
            elif "hoi" in msg.lower():
                TIMER_TEMMIE = time.time()
                TEM_CHECK = False
                send_message(msg_object.get_channel(), msg_object.get_sender() + ", " + "* hOI!!!!!! i'm tEMMIE!! temMIE")
            else:
                TIMER_TEMMIE = time.time()
                TEM_CHECK = False
                send_message(msg_object.get_channel(), msg_object.get_sender() + ", " + random.choice(response))

# ------------- Quote Commands -------------

def command_quote(msg_object):
    try:
        with open("quotes.json", "r") as q:
            quotedict = load(q)
        try:
            msg = msg_object.get_message()
            msgnum = int(msg[7:])
            quotelist = quotedict[msg_object.get_channel()]
            quotecount = quotelist['0']
            if msgnum == 0:
                send_message(msg_object.get_channel(), "There are " + str(quotecount) + " quotes for this channel")
            elif msgnum > quotecount:
                send_message(msg_object.get_channel(), "There is no quote for that number.")
            else:
                send_message(msg_object.get_channel(), quotelist[str(msgnum)])

        except ValueError:
            quotelist = quotedict[msg_object.get_channel()]
            quotecount = quotelist['0']
            if quotecount == 1:
                send_message(msg_object.get_channel(), quotelist['1'])
            else:
                send_message(msg_object.get_channel(), quotelist[str(random.randrange(1,quotecount))])

    except FileNotFoundError:
        with open("quotes.json", "w") as q:
            quotedict = {msg_object.get_channel() : {'0':1, '1':'"Nah, not feeling it." - Me'}}
            dump(quotedict, q)
            
        send_message(msg_object.get_channel(), "No quote file found, so I made you one. <3")

    except KeyError:
        with open("quotes.json", "r") as q:
            quotedict = load(q)
        with open("quotes.json", "w") as q:
            quotedict = {msg_object.get_channel() : {'0':1, '1':'"Nah, not feeling it." - Me'}}
            dump(quotedict, q)
            
        send_message(msg_object.get_channel(), "No quotes found for this channel, so I made you one. <3")

def command_write_quote(msg_object):
    try:
        with open("quotes.json", "r") as q:
            quotedict = load(q)
        with open("quotes.json", "w") as q:
            quotelist = quotedict[msg_object.get_channel()]
            msg = msg_object.get_message()
            quote = msg[12:]
            quotecount = quotelist['0'] + 1
            quotelist['0'] = quotecount
            quotelist[str(quotecount)] = quote
            quotedict[msg_object.get_channel()] = quotelist
            dump(quotedict, q)
            
        send_message(msg_object.get_channel(), "Successfully added " + quote + " to the quote list.")
            
    except FileNotFoundError:
        with open("quotes.json", "w") as q:
            msg = msg_object.get_message()
            quote = msg[12:]
            quotedict = {msg_object.get_channel() : {'0':1}}
            quotedict = {msg_object.get_channel(): {'1':quote}}
            dump(quotedict, q)
            
        send_message(msg_object.get_channel(), "Successfully added " + quote + " to the quote list.")

def command_leave(msg_object):
    """!leave forces Keewybot to quit. It is accessible only by admins or channel owners, should Keewybot
        ever find its way onto other channels that the owner doesn't want"""
    if msg_object.get_sender() in admins or msg_object.get_sender() == msg_object.get_channel[1:]:
        send_message(msg_object.get_channel(), "Keewybot is now leaving. Goodbye!")
        exit()

# ------------------- The Pet Commands -------------------------------

def command_pet_toggle(msg_object):
    """Switches petting between short and long form. Only works for mods.

str, str, str -> none"""
    global PET_BOOL
    if PET_BOOL:
        PET_BOOL = False
        send_message(msg_object.get_channel(), 'Lesser Dog got closer.')
    elif not PET_BOOL:
        PET_BOOL = True
        send_message(msg_object.get_channel(), 'Lesser Dog walked away.')
    else:
        send_message(msg_object.get_channel(), 'Invalid arguement "' + petstr + '"')


def command_pet(msg_object):
    global PET_COUNTER
    global PET_BOOL
    global TIME_SET
    if  PET_BOOL:
        send_message(msg_object.get_channel(), 'KeewyDog Lesser Dog got excited.')

    else:
        i = botcmds.pet(PET_COUNTER)
        PET_COUNTER = PET_COUNTER + 1
        TIME_SET = time.time()
        for message in i:
            send_message(msg_object.get_channel(), message)
    
# ------------- End Command Functions -----------------



# --------- Function for Starting Bot While Loop ---------

def start_bot(HOST, PORT, PASS, NICK, CHAN):
    """Takes the cfg.py settings and starts the while loop that runs the bot.

str, str, str, str, str -> none"""
    print("Starting bot login to " + CHAN)


    con.connect((HOST, PORT))
    send_pass(PASS)
    send_nick(NICK)


    join_channel(CHAN)


    data = ""

# Restating global variables cause this is now a function.
    global PET_COUNTER
    global PET_BOOL
    global TIME_SET
    global mods
    global chatters
    global SILENT_MODE
    global TEM_CHECK
    global TIMER_TEMMIE
    
#create a new state machine instance
    BotState = StateMachine()
    random.seed(time.time())

    PET_COUNTER = 0
    PET_BOOL = True
    TIME_SET = time.time()
    
    TEM_CHECK = True
    TIMER_TEMMIE = time.time()

    if CHAN not in cfg.SILENT_AUTO_OFF:
        change_state(BotState, BotState.transitions["!silent"])

    while True:
        try:       
            data = data+con.recv(1024).decode('UTF-8')
            data_split = re.split(r"[~\r\n]+", data)
            data = data_split.pop()

            if (TIME_SET - time.time()) < -30 or (TIME_SET - time.time())> 0:
                PET_COUNTER = 0
                TIME_SET = time.time()
                
            if (TIMER_TEMMIE - time.time()) < -5 or (TIMER_TEMMIE - time.time())> 0:
                TEM_CHECK = True
                TIMER_TEMMIE = time.time()

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
                        print ("Joined and loaded " + CHAN)

                    if line[0] == 'PING':
                        send_pong(line[1])

                    if line[1] == 'PRIVMSG':
                        sender = get_sender(line[0])
                        message = get_message(line)
                        parse_message(sender, message, CHAN, BotState)

                        print(sender + ": " + message)

            
            time.sleep(1 / settings.RATE)

        except socket.error:
            print("Socket died")

        except socket.timeout:
            print("Socket timeout")


# ---------- End Bot Function -----------
# _______________________________________________________________
#
# ------ Multiprocessing Testing --------


for channel in CHAN_CFG:
    if __name__ == '__main__':    # This must be here because of Windows OS
        p = Process(target=start_bot, args=(HOST_CFG, PORT_CFG, PASS_CFG, NICK_CFG, channel))
        p.start()
