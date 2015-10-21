# bot.py

import cfg, re, botcmds, socket, time, copy, pet
from multiprocessing import Process

# Make sure you prefix the quotes with an 'r'!
CHAT_MSG=re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")


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


global mods
global chatters

global admins
admins = cfg.ADMINS

global SILENT_MODE

global con
con = socket.socket()

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
            'hoi': command_hoi,}
        # put in banables and fucker words because they're technically commands
        self.modCommands = {'!togglepet': command_pet_toggle,
            '!pettoggle': command_pet_toggle,
            "!silent": change_state,
            "!modsonly": change_state,
            "!game": change_state,}

class SilentState(object):
    """the bot says nothing but still continues banning work"""
    def __init__(self):
        self.commands = {}
        # put in banables and fucker words because they're technically commands
        self.modCommands = {
            "!normal": change_state,
            "!modsonly": change_state,
            "!game": change_state,}

class ModState(object):
    """Only mods have access to all commands the bot can do"""
    def __init__(self):
        self.commands = {}
        # put in banables and fucker words because they're technically commands
        self.modCommands = {
        	'hoi': command_hoi,
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
            "!game": change_state,}

class GameState(object):
    """Only commands relevant to the game or banable actions are active"""
    def __init__(self):
        self.commands = {}
        # put in banables and fucker words because they're technically commands
        self.modCommands = {
            "!normal": change_state,
            "!silent": change_state,
            "!modsonly": change_state,}
        

def change_state(statemachine, newstate):
    statemachine.currentState = newstate()

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
        ban_msg = copy.deepcopy(msg)
        msg = msg.split(' ')
        # a copy of the original message with all the spaces removed
        ban_msg = re.sub(' ', '', ban_msg)

        for j in BANNED_WORDS:
            if j in ban_msg.lower():
                command_timeout(CHAN, sender)
                BAN_CHECK = False

        if BAN_CHECK:
            for i in FUCKER_WORDS:
                if j in ban_msg.lower():
                    command_fuckyou(CHAN, sender)
                    FUCKER_CHECK = True

        #now we check each part of the state machine
        for i in msg:
            if i.lower() in mybotstate.currentState.commands:
                mybotstate.currentState.commands[i.lower()](channel, sender)
                #TODO: will need to updae this to support commands with parameters
            elif i.lower() in mybotstate.currentState.modCommands and check_mod(channel, sender):
                if i.lower() in mybotstate.transitions:
                    #transition to next
                    change_state(mybotstate, mybotstate.transitions[i.lower()])
                else:
                    mybotstate.currentState.modCommands[i.lower()](channel, sender)


# -------------- End Helper Functions -------------------


# -------------------- Start Command Functions -----------------
# ALL COMMANDS REQUIRE CHAN AND SENDER, EVEN IF THEY DON'T USE IT
def command_test(CHAN, sender):
    """A command to test if the bot is working.

str > none"""
    send_message(CHAN, "Hope I'm not broken.")

def command_hoi(CHAN, sender):
    """hOI!

str > none"""
    send_message(CHAN, "hOI ! ! !")


def command_pikmin4(CHAN, sender):
    """A command to express the hype that is Pikmin 4.

str > none"""
    send_message(CHAN, "PIKMIN 4 CoolCat")

def command_nerd(CHAN, sender):
    """A command to poke fun at the nerds in chat.

string > none"""
    if sender in mods or sender in admins:
        send_message(CHAN, "FrankerZ ")
        send_message(CHAN, "FrankerZ FrankerZ ")
        send_message(CHAN, "FrankerZ FrankerZ FrankerZ ")
        send_message(CHAN, "FrankerZ FrankerZ ")
        send_message(CHAN, "FrankerZ ")
        send_message(CHAN, "GET FUCKO'D")
    else:
        send_message(CHAN, 'lol nerd you do not have permission to use this command.')
    
def get_mods(CHAN, sender):
    global mods
    global chatters
    response = urlopen('https://tmi.twitch.tv/group/user/' + CHAN[1:] + '/chatters')
    readable = response.read().decode('utf-8')
    chatlist = loads(readable)
    #load the moderator list
    chatters = chatlist['chatters']
    mods = chatters['moderators']
    print ("Reloaded the Modlist")
    
def check_mod(CHAN, sender):
    global mods
    global chatters
    global admins
    if sender in mods or sender in admins:
        return True
    else:
        return False

def command_am_i_a_mod(CHAN, sender):
    global mods
    global chatters
    global admins
    if sender in mods or sender in admins:
        send_message(CHAN, "Yes, " + sender + ", obviously")
    else:
        send_message(CHAN, "No, " + sender + ", you aren't")

def command_timeout(CHAN, sender):
    """Uses the /timeout command to timeout a user.

str, str > msg"""
    send_message(CHAN, '/timeout ' + sender + ' 60')
    send_message(CHAN, sender + ' timed out because of shortened link.')
    
def command_fuckyou(CHAN, sender):
    """Uses the /timeout command cause lol fuck you too.

str, str > msg"""
    send_message(CHAN, '/timeout ' + sender + ' 5')
    send_message(CHAN, sender + ' timed out because lol fuck you too.')


# ------------------- The Pet Commands -------------------------------

def command_pet_toggle(CHAN, sender):
    """Switches petting between short and long form. Only works for mods.

str, str, str -> none"""
    global PET_BOOL
    if PET_BOOL:
        PET_BOOL = False
        send_message(CHAN, 'Lesser Dog got closer.')
    elif not PET_BOOL:
        PET_BOOL = True
        send_message(CHAN, 'Lesser Dog walked away.')
    else:
        send_message(CHAN, 'Invalid arguement "' + petstr + '"')


def command_pet(CHAN, sender):
    global PET_COUNTER
    global PET_BOOL
    global TIME_SET
    if  PET_BOOL:
        send_message(CHAN, 'KeewyDog Lesser Dog got excited.')

    else:
        i = pet.pet(PET_COUNTER)
        PET_COUNTER = PET_COUNTER + 1
        TIME_SET = time.time()
        for message in i:
            send_message(CHAN, message)
    
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
    
#create a new state machine instance
    BotState = StateMachine()

    PET_COUNTER = 0
    PET_BOOL = True
    TIME_SET = time.time()

    if CHAN not in cfg.SILENT_AUTO_OFF:
        change_state(BotState, BotState.transitions["!silent"])

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
                        print ("Joined and loaded " + CHAN)

                    if line[0] == 'PING':
                        send_pong(line[1])

                    if line[1] == 'PRIVMSG':
                        sender = get_sender(line[0])
                        message = get_message(line)
                        parse_message(sender, message, CHAN, BotState)

                        print(sender + ": " + message)

            if (TIME_SET - time.time()) < -30 or (TIME_SET - time.time())> 0:
                PET_COUNTER = 0
                print("PET_COUNTER has reset.")
                TIME_SET = time.time()
            
            time.sleep(1 / botcmds.RATE)

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
