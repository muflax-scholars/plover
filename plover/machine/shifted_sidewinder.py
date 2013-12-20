# Copyright (c) 2013 muflax <mail@muflax.com>

"""Works like the Sidewinder layout, except it's all shifted up one row. It also provides double keys so you don't awkwardly have to press two keys with one finger."""

from plover.machine.base import StenotypeBase
from plover.oslayer import keyboardcontrol

KEYCODE_TO_STENO_KEY = {
    10: "S-",    # 1
    11: "T-",    # 2
    12: "P-",    # 3
    13: "H-",    # 4
    14: "*",     # 5
    15: "#",     # 6
    16: "-F",    # 7
    17: "-P",    # 8
    18: "-L",    # 9
    19: "-T",    # 0
    20: "-D",    # -
    21: "-T -D", # =

    24: "S-",    # q
    25: "K-",    # w
    26: "W-",    # e
    27: "R-",    # r
    28: "*",     # t
    29: "*",     # y
    30: "-R",    # u
    31: "-B",    # i
    32: "-G",    # o
    33: "-S",    # p
    34: "-Z",    # [
    35: "-S -Z", # ]

    38: "#",     # a
    39: "T- K-", # s
    40: "P- W-", # d
    41: "H- R-", # f
    42: "#",     # g
    43: "#",     # h
    44: "-F -R", # j
    45: "-P -B", # k
    46: "-L -G", # l
    47: "-T -S", # ;
    48: "-D -Z", # '

    53: "A- O-", # x
    54: "A-",    # c
    55: "O-",    # v

    57: "-E",    # n
    58: "-U",    # m
    59: "-E -U", # ,
}

class Stenotype(StenotypeBase):
    """Modified version of the Microsoft Sidewinder X4 keyboard machine."""

    def __init__(self, params):
        """Monitor a Microsoft Sidewinder X4 keyboard via X events."""
        StenotypeBase.__init__(self)
        self._keyboard_emulation = keyboardcontrol.KeyboardEmulation()
        self._keyboard_capture = keyboardcontrol.KeyboardCapture()
        self._keyboard_capture.key_down = self._key_down
        self._keyboard_capture.key_up = self._key_up
        self.suppress_keyboard(True)
        self._down_keys = set()
        self._released_keys = set()
        self.arpeggiate = params['arpeggiate']

    def start_capture(self):
        """Begin listening for output from the stenotype machine."""
        self._keyboard_capture.start()
        self._ready()

    def stop_capture(self):
        """Stop listening for output from the stenotype machine."""
        self._keyboard_capture.cancel()
        self._stopped()

    def suppress_keyboard(self, suppress):
        self._is_keyboard_suppressed = suppress
        self._keyboard_capture.suppress_keyboard(suppress)

    def _key_down(self, event):
        """Called when a key is pressed."""
        if (self._is_keyboard_suppressed
            and event.keystring is not None
            and not self._keyboard_capture.is_keyboard_suppressed()):
            self._keyboard_emulation.send_backspaces(1)
        self._down_keys.add(event.keycode)

    def _post_suppress(self, suppress, steno_keys):
        """Backspace the last stroke since it matched a command.

        The suppress function is passed in to prevent threading issues with the
        gui.
        """
        n = len(steno_keys)
        if self.arpeggiate:
            n += 1
        suppress(n)

    def _key_up(self, event):
        """Called when a key is released."""
        # Process the newly released key.
        self._released_keys.add(event.keystring)
        # Remove invalid released keys.
        self._released_keys = self._released_keys.intersection(self._down_keys)

        # A stroke is complete if all pressed keys have been released.
        if self._down_keys == self._released_keys:
            # Map pressed keys into steno keys and split multi-key keys into
            # individual keys.
            steno_keys = []
            for k in self._down_keys:
                if k in KEYCODE_TO_STENO_KEY:
                   steno_keys.extend(KEYCODE_TO_STENO_KEY[k].split(" "))

            self._down_keys.clear()
            self._released_keys.clear()
            self._notify(steno_keys)

    @staticmethod
    def get_option_info():
        bool_converter = lambda s: s == 'True'
        return {
            'arpeggiate': (False, bool_converter),
        }
