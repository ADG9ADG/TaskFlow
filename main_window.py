from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QStackedWidget, QFrame, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QAbstractItemView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from .repository import TaskRepository
from .dialogs import TaskDialog

STYLES = """
QMainWindow, QWidget { background: #f5f6f8; color: #20242b; font-family: 'Segoe UI'; font-size: 10pt; }
QFrame#Sidebar { background: #ffffff; border: 1px solid #e7e9ee; border-radius: 14px; }
QLabel#Brand { font-size: 19pt; font-weight: 700; color: #20242b; }
QLabel#PageTitle { font-size: 23pt; font-weight: 700; }
QLabel#Muted { color: #777f8c; }
QPushButton { background: #ffffff; border: 1px solid #e2e5eb; border-radius: 9px; padding: 9px 13px; text-align: left; }
QPushButton:hover { background: #eef1f7; }
QPushButton#Primary { background: #303b58; color: white; border: none; font-weight: 600; padding: 10px 16px; }
QPushButton#Primary:hover { background: #425174; }
QListWidget { background: transparent; border: none; outline: none; }
QListWidget::item { padding: 11px 12px; border-radius: 8px; margin: 2px 0; }
QListWidget::item:selected { background: #e9edf5; color: #263451; font-weight: 600; }
QLineEdit { background: white; border: 1px solid #e2e5eb; border-radius: 9px; padding: 10px; }
QTableWidget { background: white; border: 1px solid #e7e9ee; border-radius: 12px; gridline-color: #f0f1f4; }
QHeaderView::section { background: #fafbfc; border: none; border-bottom: 1px solid #e7e9ee; padding: 10px; color: #687080; font-weight: 600; }
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.repo = TaskRepository()
        self.setWindowTitle("TaskFlow")
        self.resize(1220, 790)
        self.setMinimumSize(980, 650)
        self.setStyleSheet(STYLES)
        root = QWidget()
        self.setCentralWidget(root)
        outer = QHBoxLayout(root)
        outer.setContentsMargins(18, 18, 18, 18)
        outer.setSpacing(16)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(225)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(16, 20, 16, 16)
        brand = QLabel("◈  TaskFlow")
        brand.setObjectName("Brand")
        side.addWidget(brand)
        subtitle = QLabel("YOUR PERSONAL WORKSPACE")
        subtitle.setObjectName("Muted")
        subtitle.setStyleSheet("font-size:8pt; letter-spacing:1px; margin-top:5px;")
        side.addWidget(subtitle)
        side.addSpacing(24)
        self.nav = QListWidget()
        self.nav.addItems(["⌂   Dashboard", "☑   My Tasks", "◷   Today", "▦   Calendar", "▣   Projects", "◉   Habits", "◴   Focus Timer", "▤   Analytics", "⚙   Settings"])
        self.nav.setCurrentRow(0)
        self.nav.currentRowChanged.connect(self.change_page)
        side.addWidget(self.nav, 1)
        foot = QLabel("PHASE 1  •  OFFLINE FIRST")
        foot.setObjectName("Muted")
        foot.setStyleSheet("font-size:8pt;")
        side.addWidget(foot)
        outer.addWidget(side)

        self.stack = QStackedWidget()
        outer.addWidget(self.stack, 1)
        self.dashboard = self.build_dashboard()
        self.tasks_page = self.build_tasks_page()
        self.placeholder = self.build_placeholder()
        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.tasks_page)
        self.stack.addWidget(self.placeholder)
        self.refresh()

    def build_dashboard(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(10, 8, 10, 8)
        top = QHBoxLayout()
        titles = QVBoxLayout()
        title = QLabel("Good to see you.")
        title.setObjectName("PageTitle")
        desc = QLabel("Here’s your productivity overview.")
        desc.setObjectName("Muted")
        titles.addWidget(title)
        titles.addWidget(desc)
        top.addLayout(titles)
        top.addStretch()
        add = QPushButton("+  New task")
        add.setObjectName("Primary")
        add.clicked.connect(self.add_task)
        top.addWidget(add)
        layout.addLayout(top)
        layout.addSpacing(20)

        cards = QHBoxLayout()
        self.stat_labels = []
        for heading in ["All tasks", "Active", "Completed"]:
            card = QFrame()
            card.setStyleSheet("QFrame {background:white; border:1px solid #e7e9ee; border-radius:12px;}")
            box = QVBoxLayout(card)
            box.setContentsMargins(18, 16, 18, 16)
            h = QLabel(heading)
            h.setObjectName("Muted")
            value = QLabel("0")
            value.setStyleSheet("font-size:25pt; font-weight:700;")
            box.addWidget(h)
            box.addWidget(value)
            cards.addWidget(card)
            self.stat_labels.append(value)
        layout.addLayout(cards)
        layout.addSpacing(20)
        row = QHBoxLayout()
        section = QVBoxLayout()
        section_title = QLabel("Your next actions")
        section_title.setStyleSheet("font-size:14pt; font-weight:700;")
        section.addWidget(section_title)
        section_hint = QLabel("Tasks saved on this device")
        section_hint.setObjectName("Muted")
        section.addWidget(section_hint)
        self.recent_list = QListWidget()
        self.recent_list.setStyleSheet("background:white; border:1px solid #e7e9ee; border-radius:12px; padding:8px;")
        section.addWidget(self.recent_list, 1)
        row.addLayout(section, 1)
        layout.addLayout(row, 1)
        return page

    def build_tasks_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(10, 8, 10, 8)
        header = QHBoxLayout()
        title = QLabel("My Tasks")
        title.setObjectName("PageTitle")
        header.addWidget(title)
        header.addStretch()
        add = QPushButton("+  New task")
        add.setObjectName("Primary")
        add.clicked.connect(self.add_task)
        header.addWidget(add)
        layout.addLayout(header)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search tasks...")
        self.search.textChanged.connect(self.refresh_tasks)
        layout.addWidget(self.search)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Task", "Due date", "Time", "Priority", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for c in range(1, 5):
            self.table.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(False)
        self.table.doubleClicked.connect(self.toggle_selected)
        layout.addWidget(self.table, 1)
        actions = QHBoxLayout()
        hint = QLabel("Tip: double-click a task row to cycle its status.")
        hint.setObjectName("Muted")
        actions.addWidget(hint)
        actions.addStretch()
        complete = QPushButton("Mark selected complete")
        complete.clicked.connect(self.complete_selected)
        delete = QPushButton("Delete selected")
        delete.clicked.connect(self.delete_selected)
        actions.addWidget(complete)
        actions.addWidget(delete)
        layout.addLayout(actions)
        return page

    def build_placeholder(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        title = QLabel("Coming in the next phase")
        title.setStyleSheet("font-size:22pt; font-weight:700;")
        note = QLabel("This section is reserved for the Phase 2–4 feature modules.")
        note.setObjectName("Muted")
        layout.addWidget(title, alignment=Qt.AlignCenter)
        layout.addWidget(note, alignment=Qt.AlignCenter)
        return page

    def change_page(self, index):
        if index == 0:
            self.stack.setCurrentWidget(self.dashboard)
        elif index == 1:
            self.stack.setCurrentWidget(self.tasks_page)
            self.refresh_tasks()
        else:
            self.stack.setCurrentWidget(self.placeholder)

    def add_task(self):
        dialog = TaskDialog(self)
        if dialog.exec():
            self.repo.create(*dialog.values())
            self.refresh()

    def refresh(self):
        total, active, done = self.repo.counts()
        for label, value in zip(self.stat_labels, [total, active, done]):
            label.setText(str(value))
        self.recent_list.clear()
        for task in self.repo.all()[:8]:
            due = f"  •  {task['due_date']} at {task['due_time']}" if task["due_date"] else ""
            item = QListWidgetItem(f"{task['title']}   [{task['priority']}]   —   {task['status']}{due}")
            self.recent_list.addItem(item)
        self.refresh_tasks()

    def refresh_tasks(self):
        if not hasattr(self, "table"):
            return
        tasks = self.repo.all(self.search.text() if hasattr(self, "search") else "")
        self.table.setRowCount(len(tasks))
        for r, task in enumerate(tasks):
            values = [task["title"], task["due_date"] or "—", task["due_time"] or "—", task["priority"], task["status"]]
            for c, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if c == 3:
                    colors = {"Urgent":"#b42318", "High":"#b54708", "Medium":"#344054", "Low":"#667085"}
                    item.setForeground(Qt.GlobalColor.darkRed if task["priority"] == "Urgent" else Qt.GlobalColor.black)
                self.table.setItem(r, c, item)
            self.table.item(r, 0).setData(Qt.UserRole, task["id"])

    def selected_task_id(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        return self.table.item(rows[0].row(), 0).data(Qt.UserRole)

    def complete_selected(self):
        task_id = self.selected_task_id()
        if task_id is None:
            QMessageBox.information(self, "Select a task", "Choose a task row first.")
            return
        self.repo.update_status(task_id, "Completed")
        self.refresh()

    def toggle_selected(self):
        task_id = self.selected_task_id()
        if task_id is None:
            return
        row = self.table.selectionModel().selectedRows()[0].row()
        status = self.table.item(row, 4).text()
        next_status = {"Not Started":"In Progress", "In Progress":"Completed", "Completed":"Not Started"}[status]
        self.repo.update_status(task_id, next_status)
        self.refresh()

    def delete_selected(self):
        task_id = self.selected_task_id()
        if task_id is None:
            QMessageBox.information(self, "Select a task", "Choose a task row first.")
            return
        answer = QMessageBox.question(self, "Delete task", "Permanently delete this task?")
        if answer == QMessageBox.Yes:
            self.repo.delete(task_id)
            self.refresh()
