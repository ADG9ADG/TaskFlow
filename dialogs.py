from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit, QDateEdit,
    QTimeEdit, QComboBox, QDialogButtonBox, QMessageBox
)
from PySide6.QtCore import QDate, QTime

class TaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create task")
        self.setMinimumWidth(430)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.title = QLineEdit()
        self.title.setPlaceholderText("e.g. Finish project proposal")
        self.description = QTextEdit()
        self.description.setPlaceholderText("Add notes (optional)")
        self.description.setFixedHeight(85)
        self.date = QDateEdit(QDate.currentDate())
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat("ddd, dd MMM yyyy")
        self.time = QTimeEdit(QTime.currentTime())
        self.time.setDisplayFormat("hh:mm AP")
        self.priority = QComboBox()
        self.priority.addItems(["Low", "Medium", "High", "Urgent"])
        form.addRow("Task title", self.title)
        form.addRow("Description", self.description)
        form.addRow("Due date", self.date)
        form.addRow("Due time", self.time)
        form.addRow("Priority", self.priority)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def validate_and_accept(self):
        if not self.title.text().strip():
            QMessageBox.warning(self, "Missing title", "Please enter a task title.")
            self.title.setFocus()
            return
        self.accept()

    def values(self):
        return (
            self.title.text().strip(),
            self.description.toPlainText().strip(),
            self.date.date().toString("yyyy-MM-dd"),
            self.time.time().toString("HH:mm"),
            self.priority.currentText()
        )
