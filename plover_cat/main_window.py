import os
import string

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QListWidgetItem
from PyQt5.QtCore import Qt
_ = lambda txt: QtCore.QCoreApplication.translate("PloverCAT", txt)

from plover_cat.plover_cat_ui import Ui_PloverCAT

from plover_cat.project import Project

class PloverCATWindow(QMainWindow, Ui_PloverCAT):
    def __init__(self, engine):
        super().__init__()

        self.project = Project(engine)
        self.project.add_listener(self.update)


        self.setupUi(self)
        self.actionOpen.triggered.connect(lambda: self.open_file('json'))
        self.actionSave_As.triggered.connect(self.save_file)
        self.actionImport_Paper.triggered.connect(lambda: self.open_file('paper'))
        self.actionImport_Raw.triggered.connect(lambda: self.open_file('raw'))
        self.actionRemove_Edit.triggered.connect(self.remove_edit)
        self.actionExport.triggered.connect(self.export)
        self.textEdit.cursorPositionChanged.connect(self.move_cursor)
        self.textEdit.setPlainText("Welcome to PloverCAT\nPlease open a file with File->Open...")
        self.textEdit.setProject(self.project)
        self.strokeList.setFocusPolicy(Qt.NoFocus)
        self.strokeList.currentRowChanged.connect(self.select_stroke)
        self.retranslateButton.clicked.connect(self.project.update)


    def update(self, project, change_position = False):
        fixed_font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)

        edited_brush = QBrush(QColor(192,192,192))

        cursor = self.textEdit.textCursor()
        original_position = cursor.position()

        self.strokeList.clear()
        for stroke_number in range(len(project.log)):
            stroke = project.log[stroke_number]

            item = QListWidgetItem(stroke.rtfcre)
            item.setFont(fixed_font)
            edit = project.edits.get(stroke_number, None)
            if not edit is None:
                item.setText(stroke.rtfcre + " (EDITED) '" + edit + "'")
                item.setBackground(edited_brush)

            self.strokeList.addItem(item)

        self.textEdit.setPlainText(project.text)
        if not change_position is False:
            cursor.setPosition(original_position + change_position)
            self.textEdit.setTextCursor(cursor)


    def select_stroke(self, stroke_number):
        """cursor = self.textEdit.textCursor()
        stroke_start_pos = self.project.log[stroke_number].start_pos
        stroke_end_pos = len(self.project.text)
        if stroke_number + 1 < len(self.project.log):
            stroke_end_pos = self.project.log[stroke_number + 1].start_pos

        position = cursor.position()
        if position < stroke_start_pos or position > stroke_end_pos:
            cursor.setPosition(stroke_start_pos)
            self.textEdit.setTextCursor(cursor)

        # This code can sometimes cause a big recursion loop - setting
        the cursor position jumps to the stroke which jumps to a
        cursor position - it needs quite a bit of thought to
        implement cleanly.
        """
        pass


    def move_cursor(self):
        stroke_number = self.project.stroke_number_from_position(
            self.textEdit.textCursor().position()
        )
        self.strokeList.setCurrentRow(stroke_number)


    def save_file(self):
        selected_file = QFileDialog.getSaveFileName(self, _("Save Transcript"), self.project.file_name, _("Transcript (*.json)"))

        file_name = selected_file[0]
        if file_name != '':
            self.project.save_file(file_name)

    def open_file(self, file_type):
        name = "Stroke Log"
        extension = "txt"

        if file_type == "json":
            name = "Transcript"
            extension = "json"

        selected_file = QFileDialog.getOpenFileName(
            self,
            _("Open " + name),
            os.getcwd(),
            _(name + "(*." + extension + ")")
        )

        file_name = selected_file[0]
        if file_type == "raw":
            self.project.open_file_raw(file_name)
        elif file_type == "paper":
            self.project.open_file_paper(file_name)
        elif file_type == "json":
            self.project.open_file_json(file_name)

    def remove_edit(self):
        current_stroke = self.strokeList.currentRow()
        del self.project.edits[current_stroke]
        self.project.update()


    def export(self):
        selected_file = QFileDialog.getSaveFileName(
            self,
            _("Export Transcript"),
            os.path.splitext(self.project.file_name)[0] + ".txt"
            , _("Transcript (*.txt)")
        )

        file_name = selected_file[0]
        if file_name != '':
            self.project.export_file(file_name)
