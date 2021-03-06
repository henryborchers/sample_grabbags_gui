import os
import typing
from time import sleep

from PySide2 import QtCore, QtWidgets, QtUiTools, QtGui
import sys
try:
    from importlib import resources
except ImportError:
    # ignored because an issue with mypy producing false positives
    # see here https://github.com/python/mypy/issues/1153
    import importlib_resources as resources  # type: ignore


class OptionsPanel(QtWidgets.QWidget):

    def __init__(
            self,
            parent: typing.Optional[QtWidgets.QWidget] = None
    ) -> None:
        super().__init__(parent)

        # Using importlib.resources.as_file and importlib.resources.files so
        # that this can be run from a zip file.
        with resources.as_file(
                resources.files('sample').joinpath('options_ui.ui')
        ) as ui_file_name:
            ui_file = QtCore.QFile(str(ui_file_name))
            try:
                ui_file.open(QtCore.QFile.ReadOnly)
                self.ui = QtUiTools.QUiLoader().load(
                    ui_file, parentWidget=self)

            finally:
                ui_file.close()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)


class Console(QtWidgets.QWidget):
    directories_entered = QtCore.Signal(list)

    def __init__(
            self,
            parent: typing.Optional[QtWidgets.QWidget] = None
    ) -> None:

        super(Console, self).__init__(parent)
        self.setAcceptDrops(True)
        with resources.as_file(
                resources.files('sample').joinpath('interface.ui')
        ) as ui_file_name:

            ui_file = QtCore.QFile(str(ui_file_name))
            try:
                ui_file.open(QtCore.QFile.ReadOnly)
                loader = QtUiTools.QUiLoader()
                self.ui = loader.load(ui_file, self)
            finally:
                ui_file.close()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)
        self._text_buffer: typing.List[str] = []
        self._document = QtGui.QTextDocument(self)
        self.ui.consoleText.setDocument(self._document)

    def check_valid_dragged_data(self, sources: typing.List[str]) -> bool:
        for s in sources:
            if not os.path.exists(s):
                return False
            if not os.path.isdir(s):
                return False
        return True

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        dirs = [u.path() for u in event.mimeData().urls()]
        if not self.check_valid_dragged_data(dirs):
            self.pop_alert("Input accepts only folders")
            event.ignore()
            return

        paths = "".join(
            f"<li>{s.path()}</li>" for s in event.mimeData().urls()
        )

        self.pop_alert(f"Do you want to bag the following directories? :\n"
                       f"<ul>{paths}</ul>"
                       )
        event.accept()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        self.write("Bagging...")
        self.directories_entered.emit([
                s.path() for s in event.mimeData().urls()
        ])
        event.accept()

    def dragLeaveEvent(self, event: QtGui.QDragLeaveEvent) -> None:
        self.write_log_buffer_to_screen()

    def clear(self) -> None:
        self._text_buffer.clear()
        self.write_log_buffer_to_screen()

    def write(self, text: str) -> None:
        self._text_buffer.append(f"<p>{text}</p>")
        self.write_log_buffer_to_screen()

    def pop_alert(self, text: str):
        self.ui.consoleText.setText(f"<h3>{text}</h3>")

    def write_log_buffer_to_screen(self) -> None:
        self._document.setHtml("\n".join(self._text_buffer))


class Demo(QtWidgets.QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        main_widget = QtWidgets.QWidget(self)
        self._layout = QtWidgets.QVBoxLayout()
        main_widget.setLayout(self._layout)

        self.options = OptionsPanel(parent=main_widget)
        self.options.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Maximum
        )

        self.console = Console(parent=main_widget)
        self.console.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Minimum
        )

        self._layout.addWidget(self.options)
        self._layout.addWidget(self.console)
        self.clearLogButton = QtWidgets.QPushButton(text="Clear Console")
        self.clearLogButton.clicked.connect(self.console.clear)
        self._layout.addWidget(self.clearLogButton)

        self.console.directories_entered.connect(self.run)
        self.setCentralWidget(main_widget)

    def run(self, paths: typing.List[str]) -> None:
        for p in paths:
            self.console.write(p)
            QtCore.QCoreApplication.processEvents()
            sleep(.1)
        self.console.write("Done")


def main() -> None:
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication(sys.argv)
    main_window = Demo()
    main_window.setWindowTitle("Grabbags GUI Demo")
    main_window.resize(640, 480)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
