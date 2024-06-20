import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QTableWidget, QHBoxLayout, QComboBox, QTableWidgetItem, QMessageBox
from PyQt6.QtCore import Qt
from database import create_connection
import students
import courses

class Main_Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Information System")
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #E8F0F2;
            }
            QLabel {
                font-family: 'Arial', sans-serif;
                color: #3B3B3B;
            }
            QLineEdit, QComboBox {
                border: 1px solid #A9A9A9;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #A1C6EA;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-family: 'Arial', sans-serif;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7EA4D6;
            }
            QTableWidget {
                background-color: #FFFFFF;
                alternate-background-color: #F1F1F1;
                gridline-color: #E0E0E0;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QHeaderView::section {
                background-color: #A1C6EA;
                color: white;
                padding: 5px;
                border: 1px solid #E0E0E0;
                font-family: 'Arial', sans-serif;
                font-size: 14px;
            }
        """)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.database_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'MySQLpassword101',
            'database': 'ssisv2_db'
        }

        self.course_fields = ['Code', 'Name']
        self.student_fields = ['StudentID', 'StudentName', 'Gender', 'Year', 'CourseCode']

        self.initialize_ui()

    def initialize_ui(self):
        self.create_course_tab()
        self.create_student_tab()

        self.populate_course_table()
        self.populate_student_table()

    def create_course_tab(self):
        course_tab = QWidget()
        course_tab_layout = QVBoxLayout(course_tab)

        title_label = QLabel("Course Management", self)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        course_tab_layout.addWidget(title_label)

        button_layout = QHBoxLayout()

        add_course_btn = QPushButton("Add Course")
        add_course_btn.clicked.connect(lambda: courses.add_course(self))
        button_layout.addWidget(add_course_btn)

        delete_course_btn = QPushButton("Delete Course")
        delete_course_btn.clicked.connect(lambda: courses.delete_course(self))
        button_layout.addWidget(delete_course_btn)

        update_course_btn = QPushButton("Update Course")
        update_course_btn.clicked.connect(lambda: courses.update_course(self))
        button_layout.addWidget(update_course_btn)

        course_tab_layout.addLayout(button_layout)

        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter by Code:", self)
        filter_layout.addWidget(filter_label)

        self.course_filter_input = QLineEdit()
        filter_layout.addWidget(self.course_filter_input)

        filter_button = QPushButton("Filter")
        filter_button.clicked.connect(self.filter_courses)
        filter_layout.addWidget(filter_button)

        course_tab_layout.addLayout(filter_layout)

        self.course_table = QTableWidget()
        self.course_table.setAlternatingRowColors(True)
        course_tab_layout.addWidget(self.course_table)

        self.tabs.addTab(course_tab, "Courses")

    def filter_courses(self):
        filter_text = self.course_filter_input.text().strip()
        if not filter_text:
            self.populate_course_table()
            return

        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM courses WHERE Code LIKE %s", ('%' + filter_text + '%',))
        filtered_courses = cursor.fetchall()
        connection.close()

        self.populate_course_table(filtered_courses)

    def populate_course_table(self, data=None):
        courses.populate_course_table(self, data)

    def create_student_tab(self):
        student_tab = QWidget()
        student_tab_layout = QVBoxLayout(student_tab)

        title_label = QLabel("Student Management", self)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        student_tab_layout.addWidget(title_label)

        button_layout = QHBoxLayout()

        add_student_btn = QPushButton("Add Student")
        add_student_btn.clicked.connect(lambda: students.add_student(self))
        button_layout.addWidget(add_student_btn)

        delete_student_btn = QPushButton("Delete Student")
        delete_student_btn.clicked.connect(lambda: students.delete_student(self))
        button_layout.addWidget(delete_student_btn)

        update_student_btn = QPushButton("Update Student")
        update_student_btn.clicked.connect(lambda: students.update_student(self))
        button_layout.addWidget(update_student_btn)

        refresh_student_btn = QPushButton("Refresh")
        refresh_student_btn.clicked.connect(self.refresh_students)
        button_layout.addWidget(refresh_student_btn)

        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter by:", self)
        filter_layout.addWidget(filter_label)

        self.filter_input = QComboBox()
        self.filter_input.addItem("All")
        self.filter_input.addItems(self.student_fields[:-1])  # Excluding CourseCode
        self.filter_input.addItem("CourseCode")
        filter_layout.addWidget(self.filter_input)

        self.filter_text = QLineEdit()
        self.filter_text.setPlaceholderText("Enter filter value")
        filter_layout.addWidget(self.filter_text)

        filter_button = QPushButton("Filter")
        filter_button.clicked.connect(self.filter_students)
        filter_layout.addWidget(filter_button)

        student_tab_layout.addLayout(button_layout)
        student_tab_layout.addLayout(filter_layout)

        self.student_table = QTableWidget()
        self.student_table.setAlternatingRowColors(True)
        student_tab_layout.addWidget(self.student_table)

        self.tabs.addTab(student_tab, "Students")

    def refresh_students(self):
        self.populate_student_table()

    def filter_students(self):
        filter_text = self.filter_text.text().strip()
        if not filter_text:
            self.populate_student_table()
            return

        filter_field = self.filter_input.currentText()

        connection = self.create_connection()
        cursor = connection.cursor()

        if filter_field == 'All':
            query = """
                SELECT * FROM students 
                WHERE StudentID LIKE %s OR StudentName LIKE %s OR Gender LIKE %s OR Year LIKE %s OR CourseCode LIKE %s
            """
            cursor.execute(query, ('%' + filter_text + '%', '%' + filter_text + '%', '%' + filter_text + '%', '%' + filter_text + '%', '%' + filter_text + '%'))
        else:
            query = f"SELECT * FROM students WHERE {filter_field} LIKE %s"
            cursor.execute(query, ('%' + filter_text + '%',))

        filtered_students = cursor.fetchall()
        connection.close()

        self.populate_student_table(filtered_students)

    def populate_student_table(self, data=None):
        students.populate_student_table(self, data)

    def get_course_codes(self):
        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS courses (Code VARCHAR(255), Name VARCHAR(255))")
        cursor.execute("SELECT Code FROM courses")
        course_codes = cursor.fetchall()
        connection.close()

        return [code[0] for code in course_codes]

    def create_connection(self):
        return create_connection(self.database_config)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main_Window()
    window.show()
    sys.exit(app.exec())
