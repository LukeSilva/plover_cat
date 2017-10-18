import os

try:
    import simplejson as json
except ImportError:
    import json

from PyQt5.QtWidgets import QMessageBox

from plover import system
from plover.steno import Stroke
from plover_cat.translate import translate_log

from plover_cat.steno_to_stroke import steno_to_stroke


class Project(object):

    FILE_INFO = "PloverCAT Transcript"

    def __init__(self, engine):
        super().__init__()
        self.engine = engine

        self.file_name = os.getcwd() + "/transcript.json"
        self.log = []
        self.edits = {}

        self.text = ""

        self.listeners = []

    def add_listener(self, func):
        self.listeners.append(func)

    def remove_listener(self, func):
        self.listeners.remove(func)

    def _update(self, change_position):
        for listener in self.listeners:
            listener(self, change_position)

    def update(self, change_position=False):
        self.text = translate_log(self.engine, self.log, self.edits)
        self._update(change_position)

    def stroke_number_from_position(self, position):
        i = 0
        while i < len(self.log) and self.log[i].start_pos <= position:
            i += 1

        return i - 1

    def insertText(self, position, text):
        stroke_number = self.stroke_number_from_position(position)

        if len(self.log) == 0:
            return

        stroke = self.log[stroke_number]
        stroke_start = stroke.start_pos
        stroke_end = stroke.end_pos

        edit = self.edits.get(stroke_number, None)

        if edit is None:
            self.edits[stroke_number] = self.text[stroke_start:position] + text + self.text[position:stroke_end]
        else:
            self.edits[stroke_number] = edit[:position - stroke_start] + text + edit[position - stroke_start:]

        # Prevent retranslating by performing the edit manually
        self.text = self.text[:position] + text + self.text[position:]

        for i in range(stroke_number + 1, len(self.log)):
            self.log[i].start_pos += len(text)
            self.log[i].end_pos += len(text)

        self._update(len(text))

    def deleteCharacter(self, position):
        stroke_number = self.stroke_number_from_position(position)

        if len(self.log) == 0:
            return

        stroke = self.log[stroke_number]
        stroke_start = stroke.start_pos
        stroke_end = stroke.end_pos

        edit = self.edits.get(stroke_number, None)

        if edit is None:
            self.edits[stroke_number] = self.text[stroke_start:position] + self.text[position + 1:stroke_end]
        else:
            self.edits[stroke_number] = edit[:position - stroke_start] + edit[position - stroke_start + 1:]

        # Prevent retranslating by performing the edit manually
        self.text = self.text[:position] + self.text[position + 1:]

        for i in range(stroke_number + 1, len(self.log)):
            self.log[i].start_pos -= 1
            self.log[i].end_pos -= 1

        self._update(-1)

    def open_file_json(self, file_name):
        try:
            f = open(file_name)
        except IOError:
            return

        json_object = json.load(f)

        if json_object["info"] != Project.FILE_INFO:
            return

        if json_object["version"] != 1:
            return

        self.file_name = file_name
        self.edits = {}
        for key in json_object["edits"]:
            self.edits[int(key)] = json_object["edits"][key]

        self.log = [steno_to_stroke(x) for x in json_object["log"]]

        f.close()

        self.update(False)

    def open_file_paper(self, file_name):

        path_info = os.path.splitext(file_name)

        try:
            f = open(file_name)
        except IOError:
            return

        self.file_name = path_info[0] + ".json"
        self.log = []
        self.edits = {}

        for line in f:
            keys = []
            for i in range(len(line)):
                if not line[i].isspace() and i < len(system.KEYS):
                    keys.append(system.KEYS[i])
            self.log.append(Stroke(keys))

        f.close()

        self.update(False)

    def open_file_raw(self, file_name):

        path_info = os.path.splitext(file_name)

        try:
            f = open(file_name)
        except IOError:
            return

        self.file_name = path_info[0] + ".json"
        self.log = [steno_to_stroke(line.strip()) for line in f]
        self.edits = {}

        f.close()

        self.update(False)



    def save_file(self, file_name):

        with open(file_name, "w") as f:
            json.dump({
                "info": Project.FILE_INFO,
                "version": 1,
                "edits": self.edits,
                "log": [stroke.rtfcre for stroke in self.log]
            }, f, indent=2)

    def export_file(self, file_name):
        # Retranslate the strokes
        self.update(False)

        # Write the text
        with open(file_name, "w") as f:
            f.write(self.text)
