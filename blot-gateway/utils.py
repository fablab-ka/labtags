import os

def list_contains(list, filter):
    for x in list:
        if filter(x):
            return True
    return False

def list_find(list, filter):
    for x in list:
        if filter(x):
            return x
    return None


if os.getenv('C','1') == '0':
    ANSI_RED = ''
    ANSI_GREEN = ''
    ANSI_YELLOW = ''
    ANSI_CYAN = ''
    ANSI_WHITE = ''
    ANSI_BLUE = ''
    ANSI_OFF = ''
else:
    ANSI_CSI = "\033["
    ANSI_RED = ANSI_CSI + '31m'
    ANSI_GREEN = ANSI_CSI + '32m'
    ANSI_YELLOW = ANSI_CSI + '33m'
    ANSI_CYAN = ANSI_CSI + '36m'
    ANSI_WHITE = ANSI_CSI + '37m'
    ANSI_BLUE = ANSI_CSI + '34m'
    ANSI_OFF = ANSI_CSI + '0m'
