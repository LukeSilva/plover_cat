from plover import system
from plover.formatting import Formatter
from plover.steno import Stroke, normalize_steno
from plover.steno_dictionary import StenoDictionary
from plover.translation import Translator, Translation


class LogTranslator(object):
    def __init__(self):
        self.instructions = []
        self.text = ''
        self.minimum_pos = 0

    def send_backspaces(self, n):
        assert n <= len(self.text)
        self.text = self.text[:-n]

        if self.minimum_pos is None:
            self.minimum_pos = len(self.text)

        if len(self.text) < self.minimum_pos:
            self.minimum_pos = len(self.text)

        self.instructions.append(('b', n))

    def send_string(self, s):
        self.text += s
        self.instructions.append(('s', s))

    def send_key_combination(self, c):
        self.instructions.append(('c', c))

    def send_engine_command(self, c):
        self.instructions.append(('e', c))


    def translate_log(self, engine, log, edits):
        formatter = Formatter()
        formatter.set_output(self)
        formatter.start_attached = True
        formatter.start_capitalized = True
        translator = Translator()
        translator.set_min_undo_length(100)
        translator.add_listener(formatter.format)

        with engine:
            translator.set_dictionary(engine.dictionaries)
            for i in range(len(log)):
                stroke = log[i]

                self.minimum_pos = len(self.text)
                translator.translate(stroke)

                j = i - 1
                while j > 0 and log[j].start_pos > self.minimum_pos:
                    log[j].start_pos = self.minimum_pos
                    j = j - 1

                stroke.start_pos = self.minimum_pos
                stroke.end_pos = len(self.text)

                edit = edits.get(i, None)
                if not (edit is None):
                    self.text = self.text[:self.minimum_pos] + edit

            return self.text


def translate_log(engine, log, edits):
    t = LogTranslator()
    return t.translate_log(engine,log, edits)
