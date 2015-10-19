# bot.py

import cfg, re, botcmds, socket, time, copy
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

mods = []

global admins
admins = cfg.ADMINS




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
        ban_msg = copy.deepcopy(msg)
        msg = msg.split(' ')
        # a copy of the original message with all the spaces removed
        ban_msg = re.sub(' ', '', ban_msg)

        for j in BANNED_WORDS:
            if j in ban_msg.lower():
                command_timeout(CHAN, sender)
                BAN_CHECK = False

        if BAN_CHECK:
            for i in msg:
                if "hoi" in i.lower():
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
                       '!pikmin4': command_pikmin4,
                       '!NERD': command_nerd,
                       '!GetMods': get_mods,
                       '!AmIAMod': check_mod,}
# !pet command moved to options_one in case of future state improvements
            options_one = {'!togglepet': command_pet_toggle,
                           '!pettoggle': command_pet_toggle,
                           '!pet': command_pet,}
     
            if msg[0] in options:
                if msg[0] == '!AmIAMod' or msg[0] == '!GetMods':
##                    options[msg[0]](CHAN, sender)
                    pass
                else:   
                    options[msg[0]](CHAN)
            elif msg[0] in options_one:
                try:
                    if msg[0] == '!togglepet' or msg[0] == '!pettoggle':
                        options_one[msg[0]](CHAN, sender, msg[1])
                    elif msg[0] == '!pet':
                        options_one[msg[0]](CHAN)
                    else:
                        options_one[msg[0]](CHAN, msg[1])
                except KeyError:
                    # Key is not present
                    send_message(CHAN, 'One parameter is required.')
                    pass


# -------------- End Helper Functions -------------------


# -------------------- Start Command Functions -----------------

def command_test(CHAN):
    """A command to test if the bot is working.

str > none"""
    send_message(CHAN, "Hope I'm not broken.")

def command_hoi(CHAN):
    """hOI!

str > none"""
    send_message(CHAN, "hOI ! ! !")


def command_pikmin4(CHAN):
    """A command to express the hype that is Pikmin 4.

str > none"""
    send_message(CHAN, "PIKMIN 4 CoolCat")

def command_nerd(CHAN):
    """A command to poke fun at the nerds in chat.

string > none"""
    send_message(CHAN, "FrankerZ ")
    send_message(CHAN, "FrankerZ FrankerZ ")
    send_message(CHAN, "FrankerZ FrankerZ FrankerZ ")
    send_message(CHAN, "FrankerZ FrankerZ ")
    send_message(CHAN, "FrankerZ ")
    send_message(CHAN, "GET FUCKO'D")
    
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

# ------------------- The Pet Commands -------------------------------

def command_pet_toggle(CHAN, name, petstr = ""):
    """Switches petting between short and long form. Only works for mods.

str, str, str -> none"""
    global PET_BOOL
    if name in mods or name in admins:
        if petstr.lower() == 'on':
            PET_BOOL = False
            print(PET_BOOL)
            send_message(CHAN, 'Lesser Dog got closer.')
        elif petstr.lower() == 'off':
            PET_BOOL = True
            print(PET_BOOL)
            send_message(CHAN, 'Lesser Dog walked away.')
        else:
            send_message(CHAN, 'Invalid arguement "' + petstr + '"')
    else:
        send_message(CHAN, 'You do not have permission to use this command.')


def command_pet(CHAN):
    global PET_COUNTER
    global PET_BOOL
    if  PET_BOOL:
        send_message(CHAN, 'Lesser Dog got excited.')

    else:
        if PET_COUNTER < 3:
            send_message(CHAN, 'KeewyDog')
            send_message(CHAN, 'Lesser Dog got excited.')
            PET_COUNTER = PET_COUNTER + 1
            TIME_SET = time.time()
            
        elif PET_COUNTER > 2 and PET_COUNTER < 6:
            send_message(CHAN, 'KeewyDog')
            send_message(CHAN, 'KeewyLesser')
            send_message(CHAN, "It's already overexcited.")
            PET_COUNTER = PET_COUNTER + 1
            
        elif PET_COUNTER > 5 and PET_COUNTER < 9:
            send_message(CHAN, 'KeewyDog')
            send_message(CHAN, 'KeewyLesser')
            send_message(CHAN, 'KeewyLesser')
            send_message(CHAN, "Lesser Dog is overstimulated.")
            PET_COUNTER = PET_COUNTER + 1
            
        elif PET_COUNTER > 8 and PET_COUNTER < 12:
            send_message(CHAN, 'KeewyLesser')
            send_message(CHAN, 'KeewyLesser')
            send_message(CHAN, 'KeewyLesser')
            send_message(CHAN, "Lesser Dog shows no sign of stopping.")
            PET_COUNTER = PET_COUNTER + 1

        elif PET_COUNTER > 11 and PET_COUNTER < 15:
            send_message(CHAN, 'KeewyLesser KeewygoD')
            send_message(CHAN, 'KeewyLesser')
            send_message(CHAN, 'KeewyLesser')
            send_message(CHAN, "You can reach Lesser Dog again.")
            PET_COUNTER = PET_COUNTER + 1

        elif PET_COUNTER > 14 and PET_COUNTER < 18:
            send_message(CHAN, 'KeewyLesser KeewyLesser')
            send_message(CHAN, 'KeewyLesser KeewygoD')
            send_message(CHAN, 'KeewyLesser')
            send_message(CHAN, "It's possible that you may have a problem.")
            PET_COUNTER = PET_COUNTER + 1
            
        elif PET_COUNTER > 17 and PET_COUNTER < 21:
            send_message(CHAN, 'KeewyLesser KeewyLesser')
            send_message(CHAN, 'KeewyLesser KeewyLesser')
            send_message(CHAN, 'KeewyLesser KeewygoD')
            send_message(CHAN, "Lesser Dog is unpettable but appreciates the attempt.")
            PET_COUNTER = PET_COUNTER + 1

        elif PET_COUNTER > 20 and PET_COUNTER < 23:
            send_message(CHAN, 'KeewyLesser KeewyLesser')
            send_message(CHAN, 'KeewyLesser KeewyLesser')
            send_message(CHAN, 'KeewyLesser KeewyLesser')
            send_message(CHAN, "Lesser Dog has gone where no dog has gone before.")
            PET_COUNTER = PET_COUNTER + 1

        elif PET_COUNTER > 22:
            send_message(CHAN, "Really...")
            PET_COUNTER = PET_COUNTER + 1
        else:
            send_message(CHAN, "Lesser Dog is broken...")

    
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

    global PET_COUNTER
    global PET_BOOL
    global TIME_SET
    
    PET_COUNTER = 0
    PET_BOOL = True
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
                        print ("Joined and loaded " + CHAN)

                    if line[0] == 'PING':
                        send_pong(line[1])

                    if line[1] == 'PRIVMSG':
                        sender = get_sender(line[0])
                        message = get_message(line)
                        parse_message(sender, message, CHAN)

                        print(sender + ": " + message)

            if (TIME_SET - time.time()) < -120 or (TIME_SET - time.time())> 0:
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
