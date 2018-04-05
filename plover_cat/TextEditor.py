import string

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QPlainTextEdit


class PloverCATEditor(QPlainTextEdit):

    def __init__(self, widget):
        super().__init__(widget)
        self._project = None


    def setProject(self, project):
        self._project = project

    def keyPressEvent(self, event):
        modifiers = event.modifiers()
        key = event.key()
        text = event.text()
        cursor = self.textCursor()
        if modifiers == QtCore.Qt.NoModifier or modifiers == QtCore.Qt.ShiftModifier:
            if text != "" and (all(c in string.printable for c in text)):
                if self._project:
                    self._project.insertText(cursor.position(), text)
                return

            if key == QtCore.Qt.Key_Backspace:
                if self._project:
                    self._project.deleteCharacter(cursor.position() - 1)
                return
                
            elif key == QtCore.Qt.Key_Delete:
                if self._project:
                    self._project.deleteCharacter(cursor.position())
                return


        super().keyPressEvent(event)
