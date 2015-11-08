# botcmds.py

# Used to hold external/long commands.

import random

global quotelist

def pet(counter):
    """Takes a number and returns a list of strings meant to be sent as a message based off of the number.

int -> list of str"""
    if counter < 3:
        return ['KeewyDog', 'Lesser Dog got excited.']
            
    elif counter > 2 and counter < 6:
        return ['KeewyDog', 'KeewyLesser', "It's already overexcited."]
            
    elif counter > 5 and counter < 9:
        return ['KeewyDog', 'KeewyLesser', 'KeewyLesser', "Lesser Dog is overstimulated"]
            
    elif counter > 8 and counter < 12:
        return ['KeewyLesser', 'KeewyLesser', 'KeewyLesser', "Lesser Dog shows no sign of stopping."]
# List of links to automatically timeout. Meant to catch bots.
BAN = ['bit.ly', 'goo.gl', '.gu.ma', 'ow.ly', ".3utilities.com", ".gotdns.", ".myftp.", "3cm.ky", "http://t.co", '.myvnc.', 'make.my/', 'bounceme.net', 'youtubee.', '.serveftp.', 'sn.im/', '/t.co']

    elif counter > 11 and counter < 15:
        return ['KeewyLesser KeewygoD', 'KeewyLesser', 'KeewyLesser', "You can reach Lesser Dog again."]

    elif counter > 14 and counter < 18:
        return ['KeewyLesser KeewyLesser', 'KeewyLesser KeewygoD', 'KeewyLesser', "It's possible that you may have a problem."]
            
    elif counter > 17 and counter < 21:
        return ['KeewyLesser KeewyLesser', 'KeewyLesser KeewyLesser', 'KeewyLesser KeewygoD', "Lesserdog is unpettable but appreciates the attempt."]

    elif counter > 20 and counter < 23:
        return ['KeewyLesser KeewyLesser', 'KeewyLesser KeewyLesser', 'KeewyLesser KeewyLesser', "Lesser Dog has gone where no dog has gone before."]

    elif counter > 22:
        return ['Really...']

