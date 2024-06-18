from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QFormLayout, QDialogButtonBox, QMessageBox, QInputDialog, QTableWidgetItem
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

def populate_course_table(main_window, data=None):
    connection = main_window.create_connection()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS courses (Code VARCHAR(255), Name VARCHAR(255))")
    if data is None:
        cursor.execute("SELECT * FROM courses")
        data = cursor.fetchall()

    main_window.course_table.clearContents()
    main_window.course_table.setRowCount(len(data))
    main_window.course_table.setColumnCount(len(main_window.course_fields))
    main_window.course_table.setHorizontalHeaderLabels(main_window.course_fields)
    for row_index, row_data in enumerate(data):
        for column_index, field in enumerate(main_window.course_fields):
            item = QTableWidgetItem(row_data[column_index])
            main_window.course_table.setItem(row_index, column_index, item)

    connection.close()

def add_course(main_window):
    dialog = QDialog(main_window)
    dialog.setWindowTitle("Add Course")

    layout = QVBoxLayout(dialog)

    course_name_input = QLineEdit()
    course_code_input = QLineEdit()

    form_layout = QFormLayout()
    form_layout.addRow("Course Code:", course_code_input)
    form_layout.addRow("Course Name:", course_name_input)

    button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)

    # Apply fun styles to buttons
    button_box.setStyleSheet("""
        QPushButton {
            background-color: #87CEEB;
            border: 2px solid #4682B4;
            border-radius: 10px;
            padding: 6px;
            font-size: 16px;
            font-weight: bold;
            color: white;
        }
        QPushButton:hover {
            background-color: #4682B4;
        }
        QPushButton:pressed {
            background-color: #1E90FF;
        }
    """)

    layout.addLayout(form_layout)
    layout.addWidget(button_box)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        course_name = course_name_input.text().strip()
        course_code = course_code_input.text().strip()

        if not course_name or not course_code:
            QMessageBox.warning(main_window, "Error", "Both course name and code are required!")
            return

        connection = main_window.create_connection()
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS courses (Name VARCHAR(255), Code VARCHAR(255))")
        cursor.execute("INSERT INTO courses (Name, Code) VALUES (%s, %s)", (course_name, course_code))
        connection.commit()
        connection.close()

        QMessageBox.information(main_window, 'Success', 'Course added successfully!')
        main_window.populate_course_table()

def delete_course(main_window):
    course_code, ok1 = QInputDialog.getText(main_window, 'Course Code', 'Enter course code:')
    if not ok1:
        return

    connection = main_window.create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT StudentID FROM students WHERE CourseCode=%s", (course_code,))
    student_ids = cursor.fetchall()
    connection.close()

    connection = main_window.create_connection()
    cursor = connection.cursor()
    for student_id in student_ids:
        cursor.execute("UPDATE students SET CourseCode='N/A' WHERE StudentID=%s", (student_id,))
    connection.commit()
    connection.close()

    connection = main_window.create_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM courses WHERE Code=%s", (course_code,))
    connection.commit()
    connection.close()

    main_window.populate_course_table()
    main_window.populate_student_table()

    QMessageBox.information(main_window, 'Success', 'Course deleted successfully!')

def update_course(main_window):
    course_code, ok1 = QInputDialog.getText(main_window, 'Course Code', 'Enter course code:')
    if not ok1:
        return

    connection = main_window.create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM courses WHERE Code=%s", (course_code,))
    course_data = cursor.fetchone()
    connection.close()

    if not course_data:
        QMessageBox.warning(main_window, 'Error', 'No course found with the provided code.')
        return

    dialog = QDialog(main_window)
    dialog.setWindowTitle("Update Course")

    layout = QVBoxLayout(dialog)

    course_name_input = QLineEdit()
    course_name_input.setText(course_data[1])
    course_name_input.setReadOnly(True)

    course_code_input = QLineEdit()
    course_code_input.setText(course_data[0])

    form_layout = QFormLayout()
    form_layout.addRow("Course Code:", course_code_input)
    form_layout.addRow("Course Name:", course_name_input)

    button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)

    # Apply fun styles to buttons
    button_box.setStyleSheet("""
        QPushButton {
            background-color: #87CEEB;
            border: 2px solid #4682B4;
            border-radius: 10px;
            padding: 6px;
            font-size: 16px;
            font-weight: bold;
            color: white;
        }
        QPushButton:hover {
            background-color: #4682B4;
        }
        QPushButton:pressed {
            background-color: #1E90FF;
        }
    """)

    layout.addLayout(form_layout)
    layout.addWidget(button_box)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        new_course_code = course_code_input.text().strip()

        if not new_course_code:
            QMessageBox.warning(main_window, "Error", "Course code cannot be empty!")
            return

        connection = main_window.create_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET CourseCode=%s WHERE CourseCode=%s", (new_course_code, course_code))
        connection.commit()
        connection.close()

        connection = main_window.create_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE courses SET Code=%s WHERE Code=%s", (new_course_code, course_code))
        connection.commit()
        connection.close()

        QMessageBox.information(main_window, 'Success', 'Course updated successfully!')
        main_window.populate_course_table()
