from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout

from plover.gui_qt.tool import Tool

from plover_cat.plover_cat_ui import Ui_PloverCAT

from plover_cat.main_window import PloverCATWindow

class PloverCAT(Tool):

    TITLE = "PloverCAT"
    ROLE = "plover_cat"
    ICON = ':/plover_cat/icon.svg'

    def __init__(self, engine):
        super().__init__(engine)

        self.setWindowFlags(Qt.Window | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        self.layout = QHBoxLayout()
        self.layout.addWidget(PloverCATWindow(engine))
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        #what does this do?
        self.finished.connect(lambda: None)
