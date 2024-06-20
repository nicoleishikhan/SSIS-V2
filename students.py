from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QFormLayout, QComboBox, QDialogButtonBox, QMessageBox, QInputDialog, QTableWidgetItem

def execute_query(main_window, query, params=()):
    connection = main_window.create_connection()
    cursor = connection.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    connection.close()
    return result

def populate_student_table(main_window, data=None):
    create_table_query = """
        CREATE TABLE IF NOT EXISTS students (
            StudentID VARCHAR(255),
            StudentName VARCHAR(255),
            Gender VARCHAR(255),
            Year VARCHAR(255),
            CourseCode VARCHAR(255)
        )
    """
    execute_query(main_window, create_table_query)

    if data is None:
        data = execute_query(main_window, "SELECT * FROM students")

    main_window.student_table.clearContents()
    main_window.student_table.setRowCount(len(data))
    main_window.student_table.setColumnCount(len(main_window.student_fields))
    main_window.student_table.setHorizontalHeaderLabels(main_window.student_fields)
    for row_index, row_data in enumerate(data):
        for column_index, field in enumerate(main_window.student_fields):
            item = QTableWidgetItem(row_data[column_index])
            main_window.student_table.setItem(row_index, column_index, item)


def add_student(main_window):
    dialog = QDialog(main_window)
    dialog.setWindowTitle("Add Student")

    layout = QVBoxLayout(dialog)

    student_id_input = QLineEdit()
    student_name_input = QLineEdit()
    gender_input = QComboBox()
    gender_input.addItems(["Male", "Female", "Other"])
    year_input = QComboBox()
    year_input.addItems(["1", "2", "3", "4"])
    course_code_input = QComboBox()
    course_codes = main_window.get_course_codes()
    course_code_input.addItems(course_codes)

    form_layout = QFormLayout()
    form_layout.addRow("Student ID:", student_id_input)
    form_layout.addRow("Student Name:", student_name_input)
    form_layout.addRow("Gender:", gender_input)
    form_layout.addRow("Year:", year_input)
    form_layout.addRow("Course Code:", course_code_input)

    button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)

    layout.addLayout(form_layout)
    layout.addWidget(button_box)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        student_id = student_id_input.text().strip()
        student_name = student_name_input.text().strip()
        gender = gender_input.currentText()
        year = year_input.currentText()
        course_code = course_code_input.currentText()

        connection = main_window.create_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE StudentID=%s", (student_id,))
        existing_student = cursor.fetchone()
        connection.close()

        if existing_student:
            QMessageBox.warning(main_window, "Warning", f"Student with ID {student_id} already exists!")
            return

        if not (student_id and student_name):
            QMessageBox.warning(main_window, "Error", "Both student ID and name are required!")
            return

        connection = main_window.create_connection()
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS students (StudentID VARCHAR(255), StudentName VARCHAR(255), Gender VARCHAR(255), Year VARCHAR(255), CourseCode VARCHAR(255))")
        cursor.execute("INSERT INTO students (StudentID, StudentName, Gender, Year, CourseCode) VALUES (%s, %s, %s, %s, %s)", (student_id, student_name, gender, year, course_code))
        connection.commit()
        connection.close()

        QMessageBox.information(main_window, 'Success', 'Student added successfully!')
        main_window.populate_student_table()

def delete_student(main_window):
    row_index = main_window.student_table.currentRow()
    if row_index == -1:
        QMessageBox.warning(main_window, 'Error', 'Please select a student to delete.')
        return

    student_id = main_window.student_table.item(row_index, 0).text()

    connection = main_window.create_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM students WHERE StudentID=%s", (student_id,))
    connection.commit()
    connection.close()

    QMessageBox.information(main_window, 'Success', 'Student deleted successfully!')
    main_window.populate_student_table()

def update_student(main_window):
    row_index = main_window.student_table.currentRow()
    if row_index == -1:
        QMessageBox.warning(main_window, 'Error', 'Please select a student to update.')
        return

    student_id = main_window.student_table.item(row_index, 0).text()

    connection = main_window.create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM students WHERE StudentID=%s", (student_id,))
    student_data = cursor.fetchone()
    connection.close()

    if not student_data:
        QMessageBox.warning(main_window, 'Error', 'No student found with the provided ID.')
        return

    dialog = QDialog(main_window)
    dialog.setWindowTitle("Update Student")

    layout = QVBoxLayout(dialog)

    student_name_input = QLineEdit()
    student_name_input.setText(student_data[1])
    student_id_input = QLineEdit()
    student_id_input.setText(student_data[0])
    student_id_input.setReadOnly(True)
    gender_input = QComboBox()
    gender_input.addItems(["Male", "Female", "Other"])
    gender_input.setCurrentText(student_data[2])
    year_input = QComboBox()
    year_input.addItems(["1", "2", "3", "4"])
    year_input.setCurrentText(student_data[3])
    course_code_input = QComboBox()
    course_codes = main_window.get_course_codes()
    course_code_input.addItems(course_codes)
    course_code_input.setCurrentText(student_data[4])

    form_layout = QFormLayout()
    form_layout.addRow("Student ID:", student_id_input)
    form_layout.addRow("Student Name:", student_name_input)
    form_layout.addRow("Gender:", gender_input)
    form_layout.addRow("Year:", year_input)
    form_layout.addRow("Course Code:", course_code_input)

    button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)

    layout.addLayout(form_layout)
    layout.addWidget(button_box)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        student_name = student_name_input.text().strip()
        gender = gender_input.currentText()
        year = year_input.currentText()
        course_code = course_code_input.currentText()

        if not student_name:
            QMessageBox.warning(main_window, "Error", "Student name cannot be empty!")
            return

        connection = main_window.create_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET StudentName=%s, Gender=%s, Year=%s, CourseCode=%s WHERE StudentID=%s", (student_name, gender, year, course_code, student_id))
        connection.commit()
        connection.close()

        QMessageBox.information(main_window, 'Success', 'Student updated successfully!')
        main_window.populate_student_table()
