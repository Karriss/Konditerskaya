import sys
import logging
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QComboBox,QDialog, QHBoxLayout,QSizePolicy,QHeaderView,
    QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QTabWidget, QTabBar, QStylePainter, QStyleOptionTab, QStyleOptionTabWidgetFrame, QStyle
)
import pymysql
from pymysql import OperationalError
from PyQt6 import QtCore
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from PyQt6.QtGui import QFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import random
from transliterate import translit
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator

logging.basicConfig(level=logging.INFO)
pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))

db_user = "db_vgu_student"
db_password = "thasrCt3pKYWAYcK"


class VerticalQTabWidget(QTabWidget):
    def __init__(self):
        super(VerticalQTabWidget, self).__init__()
        self.setTabBar(VerticalQTabBar())
        self.setTabPosition(QTabWidget.TabPosition.West)
        self.setFont(QFont("Arial", 10))  

    def paintEvent(self, event):
        painter = QStylePainter(self)
        option = QStyleOptionTabWidgetFrame()
        self.initStyleOption(option)
        option.rect = QtCore.QRect(QtCore.QPoint(self.tabBar().geometry().width(), 0), QtCore.QSize(option.rect.width(), option.rect.height()))
        painter.drawPrimitive(QStyle.PrimitiveElement.PE_FrameTabWidget, option)

class VerticalQTabBar(QTabBar):
    def __init__(self, *args, **kwargs):
        super(VerticalQTabBar, self).__init__(*args, **kwargs)
        self.setElideMode(QtCore.Qt.TextElideMode.ElideNone)
        pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
        self.setFont(QFont("Arial", 10)) 

    def tabSizeHint(self, index):
        size_hint = super(VerticalQTabBar, self).tabSizeHint(index)
        size_hint.transpose()
        return size_hint

    def paintEvent(self, event):
        painter = QStylePainter(self)
        option = QStyleOptionTab()
        for index in range(self.count()):
            self.initStyleOption(option, index)
            if QApplication.style().objectName() == "macos":
                option.shape = QTabBar.Shape.RoundedNorth
                option.position = QStyleOptionTab.TabPosition.Beginning
            else:
                option.shape = QTabBar.Shape.RoundedWest
            painter.drawControl(QStyle.ControlElement.CE_TabBarTabShape, option)
            option.shape = QTabBar.Shape.RoundedNorth
            painter.drawControl(QStyle.ControlElement.CE_TabBarTabLabel, option)
class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Вход в систему")
        self.role = None
        self.confectioner_id = None  # Store the confectioner ID

        # Set a larger size for the dialog
        self.setMinimumSize(800, 600)  # Minimum size of 800x600 pixels

        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)  # Center the layout

        # Create a widget to hold the form layout
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)  # Center the form

        # Add a label for the title
        self.Vhod_label = QLabel("Вход в учетную запись")
        self.Vhod_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)  # Center the text
        self.Vhod_label.setStyleSheet("font-size: 18px; font-weight: bold;")  # Optional: style the label
        form_layout.addWidget(self.Vhod_label)

        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите логин")  # Set placeholder text
        self.username_input.setMinimumWidth(220)  # Set maximum width to 220 pixels
        form_layout.addWidget(self.username_input, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Введите пароль")  # Set placeholder text
        self.password_input.setMinimumWidth(220)  # Set maximum width to 220 pixels
        form_layout.addWidget(self.password_input, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        # Login button
        self.login_button = QPushButton("Войти")
        self.login_button.setMinimumWidth(120)  # Set maximum width to 220 pixels
        self.login_button.clicked.connect(self.authenticate)
        form_layout.addWidget(self.login_button, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        # Add form widget to the main layout
        main_layout.addWidget(form_widget)
        self.setLayout(main_layout)

        # Apply custom styles
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f8ff;  /* Alice blue background */
                border-radius: 10px;
                padding: 20px;
            }
            QLabel {
                font-size: 14px;
                color: #333333;
            }
            QLineEdit {
                border: 1px solid #a0a0a0;
                padding: 8px;
                border-radius: 5px;
                background-color: #e6e6fa;  /* Soft lavender */
            }
            QPushButton {
                background-color: #FF69B4;  /* Thistle color */
                border: 1px solid #a0a0a0;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #dda0dd;  /* Plum color */
            }
        """)


    def authenticate(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        try:
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='db_vgu_test'
            )

            with connection.cursor() as cursor:
                # Check if the user is an admin
                if username == "kar" and password == "123":
                    self.accept()
                    self.role = "Админ"
                    return

                # Check if the user is a confectioner
                query = "SELECT idPolzovatelya, Konditer FROM polzovateli WHERE Login = %s AND Parol = %s"
                cursor.execute(query, (username, password))
                result = cursor.fetchone()

                if result:
                    self.accept()
                    self.role = "Кондитер"
                    self.confectioner_id = result[1]  # Store the confectioner ID
                else:
                    QMessageBox.warning(self, "Ошибка", "Неверные учетные данные.")

        except OperationalError as e:
            logging.error(f"Ошибка подключения к базе данных: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка подключения к базе данных: {e}")

        finally:
            if 'connection' in locals():
                connection.close()

class ConfectionerWindow(QMainWindow):
    def __init__(self, confectioner_id):
        super().__init__()
        self.setWindowTitle("Кондитерский интерфейс")

        # Use the custom tab widget
        self.tabs = VerticalQTabWidget()

        # Create tabs with the role 'Кондитер'
        self.confectioner_tab = ConfectionerTab(role="Кондитер")
        self.completed_orders_tab = CompletedOrdersTab()
        self.order_tab = OrderTab(self.completed_orders_tab, confectioner_id, "Кондитер")  # Pass role as "Кондитер"

        # Add only the necessary tabs to the tab widget
        self.tabs.addTab(self.order_tab, "Текущие заказы")
        self.tabs.addTab(self.confectioner_tab, "Кондитеры")

        # Set the central widget
        self.setCentralWidget(self.tabs)
class AddConfectionerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить кондитера")

        # Create main vertical layout for the dialog
        main_layout = QVBoxLayout()

        # Create a horizontal layout for the name, experience, and status
        input_layout = QHBoxLayout()
        
        # Create a grid layout to align labels and inputs
        grid_layout = QVBoxLayout()
        
        # Name input
        self.name_label = QLabel("ФИО:")
        self.name_input = QLineEdit()
        self.name_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Set a regular expression validator to allow only letters and spaces
        regex = QRegularExpression("[А-Яа-яA-Za-z ]+")
        validator = QRegularExpressionValidator(regex)
        self.name_input.setValidator(validator)

        # Experience input
        self.experience_label = QLabel("Стаж:")
        self.experience_input = QLineEdit()
        self.experience_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Status input
        self.status_label = QLabel("Статус:")
        self.status_combo = QComboBox()
        self.load_statuses()  # Load statuses into the combo box

        # Add widgets to grid layout
        grid_layout.addWidget(self.name_label)
        grid_layout.addWidget(self.name_input)
        grid_layout.addWidget(self.experience_label)
        grid_layout.addWidget(self.experience_input)
        grid_layout.addWidget(self.status_label)
        grid_layout.addWidget(self.status_combo)
        
        # Add grid layout to input layout
        input_layout.addLayout(grid_layout)
        
        # Add button with some spacing
        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.add_confectioner)
        input_layout.addSpacing(20)  # Add spacing between inputs and button
        input_layout.addWidget(self.add_button)

        # Add input layout to the main layout
        main_layout.addLayout(input_layout)

        # Set layout for the dialog
        self.setLayout(main_layout)
    def load_statuses(self):
        """Loads the statuses into the combo box."""
        try:
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='db_vgu_test'
            )

            with connection.cursor() as cursor:
                query = "SELECT idStatusa, Status FROM statusy"
                cursor.execute(query)
                results = cursor.fetchall()

                self.status_combo.clear()
                for row in results:
                    self.status_combo.addItem(row[1], userData=row[0])

        except OperationalError as e:
            logging.error(f"Ошибка загрузки статусов: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки статусов: {e}")

        finally:
            if 'connection' in locals():
                connection.close()
    def generate_login(self, name):
        """Generates a login based on the full name, transliterated to English."""
        # Transliterate the name to English
        transliterated_name = translit(name, 'ru', reversed=True)
        parts = transliterated_name.split()
        if len(parts) >= 2:
            return parts[0][0].lower() + parts[1].lower()
        return transliterated_name.lower()

    def generate_password(self):
        """Generates a random 4-digit password."""
        return ''.join(random.choices('0123456789', k=4))
    def add_confectioner(self):
        """Adds a new confectioner to the database."""
        name = self.name_input.text().strip()
        experience = self.experience_input.text().strip()
        status_id = self.status_combo.currentData()

        if not name:
            QMessageBox.warning(self, "Ошибка ввода", "Пожалуйста, введите ФИО.")
            return

        if not experience.isdigit():
            QMessageBox.warning(self, "Ошибка ввода", "Стаж должен быть числом.")
            return

        login = self.generate_login(name)
        password = self.generate_password()

        try:
            logging.info("Подключение к базе данных для добавления кондитера...")
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='db_vgu_test'
            )

            with connection.cursor() as cursor:
                # Insert confectioner
                query = "INSERT INTO `konditers` (`FIO`, `Stazh`, `Status`) VALUES (%s, %s, %s)"
                cursor.execute(query, (name, experience, status_id))
                confectioner_id = cursor.lastrowid

                # Insert user
                query = "INSERT INTO `polzovateli` (`login`, `parol`, `konditer`) VALUES (%s, %s, %s)"
                cursor.execute(query, (login, password, confectioner_id))

                connection.commit()

            QMessageBox.information(self, "Успех", f"Кондитер успешно добавлен.\nЛогин: {login}\nПароль: {password}")
            self.parent().load_confectioners()  # Refresh the table after adding
            self.accept()  # Close the dialog

        except OperationalError as e:
            logging.error(f"Ошибка добавления кондитера: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка добавления кондитера: {e}")

        except Exception as e:
            logging.error(f"Неизвестная ошибка: {e}")
            QMessageBox.critical(self, "Ошибка", f"Неизвестная ошибка: {e}")

        finally:
            if 'connection' in locals():
                connection.close()
                logging.info("Соединение закрыто после добавления кондитера.")
class DeleteConfectionerDialog(QDialog): 
    def __init__(self, parent=None): 
        super().__init__(parent) 
        self.setWindowTitle("Удалить кондитера") 
 
        # Create main layout for the dialog 
        main_layout = QVBoxLayout() 
 
        # Label for selecting confectioner 
        self.confectioner_label = QLabel("Выберите кондитера:") 
        main_layout.addWidget(self.confectioner_label) 
        
        # Create horizontal layout for combo box and delete button
        h_layout = QHBoxLayout() 
        self.confectioner_combo = QComboBox() 
        self.load_confectioners() 

        # Add combo box to horizontal layout
        h_layout.addWidget(self.confectioner_combo) 
        
        # Add delete button 
        self.delete_button = QPushButton("Удалить") 
        self.delete_button.clicked.connect(self.delete_confectioner) 
        h_layout.addWidget(self.delete_button) 

        # Add horizontal layout to main layout
        main_layout.addLayout(h_layout) 
 
        # Set layout for the dialog 
        self.setLayout(main_layout) 
 
    def load_confectioners(self): 
        """Loads the confectioners into the combo box.""" 
        try: 
            connection = pymysql.connect( 
                host='5.183.188.132', 
                user=db_user, 
                password=db_password, 
                database='db_vgu_test' 
            ) 
 
            with connection.cursor() as cursor: 
                query = "SELECT idKonditera, FIO FROM konditers"
                cursor.execute(query) 
                results = cursor.fetchall() 
 
                self.confectioner_combo.clear() 
                for row in results: 
                    self.confectioner_combo.addItem(row[1], userData=row[0]) 
 
        except OperationalError as e: 
            logging.error(f"Ошибка загрузки кондитеров: {e}") 
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки кондитеров: {e}") 
 
        finally: 
            if 'connection' in locals(): 
                connection.close() 
 
    def delete_confectioner(self):
        """Deletes the selected confectioner from the database."""
        confectioner_id = self.confectioner_combo.currentData()
        if confectioner_id is not None:
            try:
                connection = pymysql.connect(
                    host='5.183.188.132',
                    user=db_user,
                    password=db_password,
                    database='db_vgu_test'
                )

                with connection.cursor() as cursor:
                    # Check for references in the 'zakazy' table
                    query = """
                    SELECT COUNT(*) FROM zakazy
                    WHERE Konditer = %s
                    """
                    cursor.execute(query, (confectioner_id,))
                    count = cursor.fetchone()[0]

                    if count > 0:
                        QMessageBox.warning(self, "Ошибка", "Невозможно удалить кондитера, так как он связан с другими записями.")
                        return

                    # Proceed with deletion if no references are found
                    # First, delete the user account associated with the confectioner
                    query = "DELETE FROM polzovateli WHERE Konditer = %s"
                    cursor.execute(query, (confectioner_id,))

                    # Then, delete the confectioner
                    query = "DELETE FROM konditers WHERE idKonditera = %s"
                    cursor.execute(query, (confectioner_id,))
                    connection.commit()

                QMessageBox.information(self, "Успех", "Кондитер и его аккаунт успешно удалены.")
                self.parent().load_confectioners()  # Refresh the table after deletion
                self.accept()  # Close the dialog

            except OperationalError as e:
                logging.error(f"Ошибка удаления кондитера: {e}")
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления кондитера: {e}")

            finally:
                if 'connection' in locals():
                    connection.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите кондитера для удаления.")
class EditConfectionerDialog(QDialog):
    def __init__(self, confectioner_id, name, experience, status_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать кондитера")
        self.confectioner_id = confectioner_id

        # Create main layout
        main_layout = QVBoxLayout()

        # Name input
        self.name_label = QLabel("ФИО:")
        self.name_input = QLineEdit(name)
        self.name_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Experience input
        self.experience_label = QLabel("Стаж:")
        self.experience_input = QLineEdit(str(experience))
        self.experience_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Status input
        self.status_label = QLabel("Статус:")
        self.status_combo = QComboBox()
        self.load_statuses(status_id)

        # Add widgets to layout
        main_layout.addWidget(self.name_label)
        main_layout.addWidget(self.name_input)
        main_layout.addWidget(self.experience_label)
        main_layout.addWidget(self.experience_input)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.status_combo)

        # Save button
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_confectioner)
        main_layout.addWidget(self.save_button)

        # Set layout
        self.setLayout(main_layout)

    def load_statuses(self, current_status_id):
        """Loads the statuses into the combo box and sets the current status."""
        try:
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='db_vgu_test'
            )

            with connection.cursor() as cursor:
                query = "SELECT idStatusa, Status FROM statusy"
                cursor.execute(query)
                results = cursor.fetchall()

                self.status_combo.clear()
                for row in results:
                    self.status_combo.addItem(row[1], userData=row[0])
                    if row[0] == current_status_id:
                        self.status_combo.setCurrentIndex(self.status_combo.count() - 1)

        except OperationalError as e:
            logging.error(f"Ошибка загрузки статусов: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки статусов: {e}")

        finally:
            if 'connection' in locals():
                connection.close()

    def save_confectioner(self):
        """Saves the edited confectioner details to the database."""
        new_name = self.name_input.text().strip()
        new_experience = self.experience_input.text().strip()
        new_status_id = self.status_combo.currentData()

        if not new_name:
            QMessageBox.warning(self, "Ошибка ввода", "Пожалуйста, введите ФИО.")
            return

        if not new_experience.isdigit():
            QMessageBox.warning(self, "Ошибка ввода", "Стаж должен быть числом.")
            return

        try:
            logging.info("Подключение к базе данных для обновления кондитера...")
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='db_vgu_test'
            )

            with connection.cursor() as cursor:
                query = """
                UPDATE `konditers`
                SET `FIO` = %s, `Stazh` = %s, `Status` = %s
                WHERE `idKonditera` = %s
                """
                cursor.execute(query, (new_name, new_experience, new_status_id, self.confectioner_id))
                connection.commit()

            QMessageBox.information(self, "Успех", "Кондитер успешно обновлен.")
            self.accept()  # Close the dialog

        except OperationalError as e:
            logging.error(f"Ошибка обновления кондитера: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка обновления кондитера: {e}")

        finally:
            if 'connection' in locals():
                connection.close()
                logging.info("Соединение закрыто после обновления кондитера.")
class ConfectionerTab(QWidget):
    def __init__(self, role):
        super().__init__()
        self.role = role  # Initialize the role attribute

        # Create main horizontal layout for the tab
        main_layout = QHBoxLayout()

        # Table to display confectioners
        self.confectioner_table = QTableWidget()
        self.confectioner_table.setColumnCount(3)  # Add column for status
        self.confectioner_table.setHorizontalHeaderLabels(["ФИО", "Стаж", "Статус"])
        self.confectioner_table.horizontalHeader().setStretchLastSection(True)
        self.confectioner_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.confectioner_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.confectioner_table.cellDoubleClicked.connect(self.open_edit_confectioner_dialog)

        # Adjust column widths for better proportions
        self.confectioner_table.setColumnWidth(0, 800)  # ФИО
        self.confectioner_table.setColumnWidth(1, 200)  # Стаж
        self.confectioner_table.setColumnWidth(2, 150)  # Статус

        # Create a vertical layout for buttons
        button_layout = QVBoxLayout()

        # Add buttons only if the user is an admin
        if role == "Админ":
            # Buttons for adding and deleting confectioners
            self.add_button = QPushButton("Добавить кондитера")
            self.add_button.clicked.connect(self.show_add_confectioner_dialog)

            self.delete_button = QPushButton("Удалить кондитера")
            self.delete_button.clicked.connect(self.show_delete_confectioner_dialog)

            # Add buttons to button layout
            button_layout.addWidget(self.add_button)
            button_layout.addWidget(self.delete_button)

        button_layout.addStretch()  # Add stretch to push buttons to the top

        # Add table and button layout to main layout
        main_layout.addWidget(self.confectioner_table)
        main_layout.addLayout(button_layout)

        # Set layout for the tab
        self.setLayout(main_layout)

        # Load data
        self.load_confectioners()

    def open_edit_confectioner_dialog(self, row, column):
        """Opens the dialog to edit a confectioner."""
        # Only allow editing if the role is "Админ"
        if self.role == "Админ":
            confectioner_id = self.confectioner_table.item(row, 0).data(QtCore.Qt.ItemDataRole.UserRole)
            name = self.confectioner_table.item(row, 0).text()
            experience = self.confectioner_table.item(row, 1).text()
            status = self.confectioner_table.item(row, 2).data(QtCore.Qt.ItemDataRole.UserRole)

            dialog = EditConfectionerDialog(confectioner_id, name, experience, status, self)
            if dialog.exec():
                self.load_confectioners()

    def show_add_confectioner_dialog(self):
        """Shows the dialog to add a new confectioner."""
        dialog = AddConfectionerDialog(self)
        dialog.exec()

    def show_delete_confectioner_dialog(self):
        """Shows the dialog to delete a confectioner."""
        dialog = DeleteConfectionerDialog(self)
        dialog.exec()

    def load_confectioners(self):
        """Loads the confectioners from the database into the table."""
        try:
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='db_vgu_test'
            )

            with connection.cursor() as cursor:
                query = """
                SELECT konditers.idKonditera, konditers.FIO, konditers.Stazh, statusy.Status
                FROM konditers
                JOIN statusy ON konditers.Status = statusy.idStatusa
                """
                cursor.execute(query)
                results = cursor.fetchall()

                self.confectioner_table.setRowCount(len(results))
                for row_index, row_data in enumerate(results):
                    item = QTableWidgetItem(row_data[1])
                    item.setData(QtCore.Qt.ItemDataRole.UserRole, row_data[0])
                    self.confectioner_table.setItem(row_index, 0, item)
                    self.confectioner_table.setItem(row_index, 1, QTableWidgetItem(str(row_data[2])))
                    self.confectioner_table.setItem(row_index, 2, QTableWidgetItem(row_data[3]))

        except OperationalError as e:
            logging.error(f"Ошибка загрузки кондитеров: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки кондитеров: {e}")

        finally:
            if 'connection' in locals():
                connection.close()

    def delete_confectioner(self):
        """Deletes the selected confectioner from the database."""
        selected_row = self.confectioner_table.currentRow()
        if selected_row >= 0:
            name = self.confectioner_table.item(selected_row, 0).text()
            try:
                connection = pymysql.connect(
                    host='5.183.188.132',
                    user=db_user,
                    password=db_password,
                    database='db_vgu_test'
                )

                with connection.cursor() as cursor:
                    query = "DELETE FROM `konditers` WHERE `FIO` = %s"
                    cursor.execute(query, (name,))
                    connection.commit()

                QMessageBox.information(self, "Успех", "Кондитер успешно удален.")
                self.load_confectioners()  # Refresh the table after deletion

            except OperationalError as e:
                logging.error(f"Ошибка удаления кондитера: {e}")
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления кондитера: {e}")

            finally:
                if 'connection' in locals():
                    connection.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите кондитера для удаления.")
class AddProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить товар")

        # Создаем основные вертикальные и сеточные макеты
        main_layout = QVBoxLayout()
        grid_layout = QVBoxLayout()

        # Ввод наименования
        self.name_label = QLabel("Наименование:")
        self.name_input = QLineEdit()
        self.name_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Ввод цены
        self.price_label = QLabel("Цена:")
        self.price_input = QLineEdit()
        self.price_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Ввод количества
        self.quantity_label = QLabel("Количество:")
        self.quantity_input = QLineEdit()
        self.quantity_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Добавление элементов в сетку
        grid_layout.addWidget(self.name_label)
        grid_layout.addWidget(self.name_input)
        grid_layout.addWidget(self.price_label)
        grid_layout.addWidget(self.price_input)
        grid_layout.addWidget(self.quantity_label)
        grid_layout.addWidget(self.quantity_input)

        # Кнопка для добавления товара
        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.add_product)

        # Добавление кнопки в основной макет
        main_layout.addLayout(grid_layout)
        main_layout.addWidget(self.add_button)

        # Устанавливаем макет для диалога
        self.setLayout(main_layout)

    def add_product(self):
        """Добавление нового товара в базу данных."""
        name = self.name_input.text().strip()
        price = self.price_input.text().strip()
        quantity = self.quantity_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Ошибка ввода", "Пожалуйста, введите наименование.")
            return

        if not price.isdigit():
            QMessageBox.warning(self, "Ошибка ввода", "Цена должна быть числом.")
            return

        if not quantity.isdigit():
            QMessageBox.warning(self, "Ошибка ввода", "Количество должно быть числом.")
            return

        try:
            logging.info("Подключение к базе данных для добавления товара...")
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='db_vgu_test'
            )

            with connection.cursor() as cursor:
                query = "INSERT INTO `tovari` (`Naimenovanie`, `Tsenza`, `Kolichestvo`) VALUES (%s, %s, %s)"
                cursor.execute(query, (name, price, quantity))
                connection.commit()

            QMessageBox.information(self, "Успех", "Товар успешно добавлен.")
            self.parent().load_products()  # Обновляем таблицу товаров
            self.accept()  # Закрываем диалог

        except OperationalError as e:
            logging.error(f"Ошибка добавления товара: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка добавления товара: {e}")

        except Exception as e:
            logging.error(f"Неизвестная ошибка: {e}")
            QMessageBox.critical(self, "Ошибка", f"Неизвестная ошибка: {e}")

        finally:
            if 'connection' in locals():
                connection.close()
                logging.info("Соединение закрыто после добавления товара.")
class ProductTab(QWidget):
    def __init__(self):
        super().__init__()

        # Create main vertical layout for the tab
        main_layout = QVBoxLayout()

        # Create horizontal layout for search input and buttons
        search_and_button_layout = QHBoxLayout()

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск товаров...")
        self.search_input.textChanged.connect(self.filter_products)

        # Button to add a product
        self.add_product_button = QPushButton("Добавить товар")
        self.add_product_button.clicked.connect(self.open_add_product_dialog)

        # Button to generate report
        self.report_button = QPushButton("Сформировать отчет")
        self.report_button.clicked.connect(self.generate_report)

        # Add search input and buttons to the horizontal layout
        search_and_button_layout.addWidget(self.search_input)
        search_and_button_layout.addWidget(self.add_product_button)
        search_and_button_layout.addWidget(self.report_button)

        # Table to display products
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(4)  # Наименование, Цена, Количество, Удалить
        self.product_table.setHorizontalHeaderLabels(["Наименование", "Цена", "Количество", "Удалить"])
        self.product_table.horizontalHeader().setStretchLastSection(True)
        self.product_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.product_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Connect double-click event to open edit dialog
        self.product_table.cellDoubleClicked.connect(self.open_edit_product_dialog)

        # Adjust column widths
        header = self.product_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Add horizontal layout and table to main layout
        main_layout.addLayout(search_and_button_layout)
        main_layout.addWidget(self.product_table)

        # Set layout for the tab
        self.setLayout(main_layout)

        # Load products from the database
        self.load_products()
    def on_tab_changed(self, index):
        """Reload products when the tab is changed to the ProductTab."""
        # Get the QTabWidget parent
        tab_widget = self.parentWidget()
        if tab_widget and tab_widget.currentWidget() == self:
            self.load_products()
    def open_edit_product_dialog(self, row, column):
        """Opens the dialog to edit a product."""
        product_name = self.product_table.item(row, 0).text()
        price = self.product_table.item(row, 1).text()
        quantity = self.product_table.item(row, 2).text()

        dialog = EditProductDialog(product_name, price, quantity, self)
        if dialog.exec():
            self.load_products()  # Reload products after editing
    def open_add_product_dialog(self):
        """Открывает диалог для добавления товара."""
        dialog = AddProductDialog(self)
        if dialog.exec():  # Если пользователь подтвердил добавление
            self.load_products()  # Перезагрузить список товаров

    def load_products(self):
        """Загружает товары из базы данных и добавляет кнопку для удаления."""
        try:
            logging.info("Подключение к базе данных для загрузки товаров...")
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='db_vgu_test'
            )

            with connection.cursor() as cursor:
                query = "SELECT `Naimenovanie`, `Tsenza`, `Kolichestvo` FROM `tovari`"
                cursor.execute(query)
                self.products = cursor.fetchall()  # Store products for filtering

            self.display_products(self.products)

            logging.info("Загрузка товаров завершена.")

        except pymysql.OperationalError as e:
            logging.error(f"Ошибка загрузки товаров: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка подключения к базе данных: {e}")

        except Exception as e:
            logging.error(f"Неизвестная ошибка: {e}")
            QMessageBox.critical(self, "Ошибка", f"Неизвестная ошибка: {e}")

        finally:
            if 'connection' in locals():
                connection.close()
                logging.info("Соединение закрыто после загрузки товаров.")

    def display_products(self, products):
        """Displays the given list of products in the table."""
        self.product_table.setRowCount(0)  # Clear the table

        for row_idx, product in enumerate(products):
            self.product_table.insertRow(row_idx)

            # Set product details
            self.product_table.setItem(row_idx, 0, QTableWidgetItem(product[0]))
            self.product_table.setItem(row_idx, 1, QTableWidgetItem(str(product[1])))
            self.product_table.setItem(row_idx, 2, QTableWidgetItem(str(product[2])))

            # Add delete button
            delete_button = QPushButton("❌")
            delete_button.setToolTip(f"Удалить {product[0]}")
            delete_button.clicked.connect(self._create_delete_handler(product[0]))
            self.product_table.setCellWidget(row_idx, 3, delete_button)

    def filter_products(self):
        """Filters the products based on the search input."""
        search_query = self.search_input.text().lower()
        filtered_products = [product for product in self.products if search_query in product[0].lower()]
        self.display_products(filtered_products)

    def _create_delete_handler(self, product_name):
        """Создает обработчик для удаления конкретного товара."""
        def delete_product():
            try:
                logging.info(f"Проверка ссылок на товар '{product_name}' перед удалением...")
                connection = pymysql.connect(
                    host='5.183.188.132',
                    user=db_user,
                    password=db_password,
                    database='db_vgu_test'
                )

                with connection.cursor() as cursor:
                    # Check if the product is referenced in `sostavzakaza`
                    query = "SELECT COUNT(*) FROM sostavzakaza WHERE Tovar = (SELECT idTovara FROM tovari WHERE Naimenovanie = %s)"
                    cursor.execute(query, (product_name,))
                    count = cursor.fetchone()[0]

                    if count > 0:
                        QMessageBox.warning(self, "Ошибка", f"Товар '{product_name}' не может быть удален, так как он используется в заказах.")
                        return

                # Proceed with deletion if no references are found
                confirm = QMessageBox(self)
                confirm.setWindowTitle("Подтверждение")
                confirm.setText(f"Вы уверены, что хотите удалить товар '{product_name}'?")
                confirm.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                confirm.button(QMessageBox.StandardButton.Yes).setText("Да")
                confirm.button(QMessageBox.StandardButton.No).setText("Нет")

                if confirm.exec() == QMessageBox.StandardButton.Yes:
                    with connection.cursor() as cursor:
                        query = "DELETE FROM `tovari` WHERE `Naimenovanie` = %s"
                        cursor.execute(query, (product_name,))
                        connection.commit()

                    QMessageBox.information(self, "Успех", f"Товар '{product_name}' успешно удален.")
                    self.load_products()  # Обновление таблицы после удаления

            except pymysql.OperationalError as e:
                logging.error(f"Ошибка удаления товара: {e}")
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления товара: {e}")

            except Exception as e:
                logging.error(f"Неизвестная ошибка: {e}")
                QMessageBox.critical(self, "Ошибка", f"Неизвестная ошибка: {e}")

            finally:
                if 'connection' in locals():
                    connection.close()
                    logging.info("Соединение закрыто после удаления товара.")

        return delete_product
    def generate_report(self, *args):
        """Generates a PDF report of completed orders for the current month."""
        try:
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='db_vgu_test',
                charset='utf8mb4'  # Ensure the database connection uses the correct charset
            )

            with connection.cursor() as cursor:
                # Get the current month and year
                current_month = datetime.now().month
                current_year = datetime.now().year

                # Query to get completed orders for the current month
                query = """
                SELECT 
                    tovari.Naimenovanie,
                    SUM(zakazy.Kolichestvo) AS KolichestvoProdannykh,
                    SUM(zakazy.Kolichestvo * tovari.Tsenza) AS ItogovayaTsena
                FROM zakazy
                JOIN statusyzakazov ON zakazy.Status = statusyzakazov.idStatusaZakaza
                JOIN sostavzakaza ON zakazy.idZakaza = sostavzakaza.Zakaz
                JOIN tovari ON sostavzakaza.Tovar = tovari.idTovara
                WHERE statusyzakazov.StatusZakaza = 'vipolnen'
                AND MONTH(zakazy.DataOformleniya) = %s
                AND YEAR(zakazy.DataOformleniya) = %s
                GROUP BY tovari.Naimenovanie
                """
                cursor.execute(query, (current_month, current_year))
                completed_orders = cursor.fetchall()

            # Calculate the total sum of all orders
            total_sum = sum(order[2] for order in completed_orders)

            # Generate PDF
            pdf_filename = f"Отchet_zavershennye_zakazy_{current_year}_{current_month}.pdf"
            c = canvas.Canvas(pdf_filename, pagesize=letter)
            c.setFont("Arial", 12)  # Use the registered TrueType font
            c.drawString(100, 750, f"Отчет по завершенным заказам за {current_month}/{current_year}")

            y_position = 720
            for order in completed_orders:
                order_details = f"Наименование: {order[0]}, Количество: {order[1]}, Итоговая Цена: {order[2]:.2f}"
                c.drawString(100, y_position, order_details)
                y_position -= 20
                if y_position < 50:
                    c.showPage()
                    y_position = 750

            # Add the total sum at the bottom of the report
            if y_position < 50:
                c.showPage()
                y_position = 750
            c.drawString(100, y_position, f"Итоговая сумма: {total_sum:.2f}")

            c.save()
            logging.info(f"Report generated: {pdf_filename}")
            QMessageBox.information(self, "Успех", f"Отчет успешно сформирован: {pdf_filename}")

        except pymysql.OperationalError as e:
            logging.error(f"Ошибка генерации отчета: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка генерации отчета: {e}")

        except Exception as e:
            logging.error(f"Неизвестная ошибка: {e}")
            QMessageBox.critical(self, "Ошибка", f"Неизвестная ошибка: {e}")

        finally:
            if 'connection' in locals():
                connection.close()
class OrderTab(QWidget):
    def __init__(self, completed_orders_tab, logged_in_confectioner_id, role):
        super().__init__()
        self.completed_orders_tab = completed_orders_tab
        self.logged_in_confectioner_id = logged_in_confectioner_id
        self.role = role  # Store the user's role

        # Create layout for the tab
        main_layout = QVBoxLayout()

        # Table to display orders
        self.order_table = QTableWidget()
        self.order_table.setColumnCount(8)
        self.order_table.setHorizontalHeaderLabels([
            "Дата Оформления", "Дата Выдачи", "Наименование", "Количество", "Итоговая Цена", "Кондитер", "Заказчик", "Статус"
        ])
        self.order_table.horizontalHeader().setStretchLastSection(True)
        self.order_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.order_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Add table to main layout
        main_layout.addWidget(self.order_table)
        self.order_table.setColumnWidth(0, 150)
        # Set layout for the tab
        self.setLayout(main_layout)

        # Load orders from the database
        self.load_orders()

    def mark_order_completed(self, order_id):
        """Marks the order as completed if the logged-in confectioner is responsible for it or if the user is an admin."""
        try:
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='db_vgu_test'
            )

            with connection.cursor() as cursor:
                # Check if the logged-in confectioner is responsible for the order
                query = "SELECT Konditer FROM zakazy WHERE idZakaza = %s"
                cursor.execute(query, (order_id,))
                result = cursor.fetchone()

                if not result or (result[0] != self.logged_in_confectioner_id and self.role != "Админ"):
                    QMessageBox.warning(self, "Ошибка", "Вы можете завершить только свои заказы.")
                    return

                # Proceed with marking the order as completed
                cursor.execute("SELECT idStatusaZakaza FROM statusyzakazov WHERE StatusZakaza = 'vipolnen'")
                status_id = cursor.fetchone()[0]

                query = "UPDATE zakazy SET Status = %s WHERE idZakaza = %s"
                cursor.execute(query, (status_id, order_id))
                connection.commit()

            QMessageBox.information(self, "Успех", "Заказ успешно завершен.")
            self.load_orders()
            if self.completed_orders_tab is not None:
                self.completed_orders_tab.load_completed_orders()

        except OperationalError as e:
            logging.error(f"Ошибка обновления статуса заказа: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка обновления статуса заказа: {e}")

        finally:
            if 'connection' in locals():
                connection.close()

    def load_orders(self):
        """Loads the orders from the database into the table."""
        try:
            logging.info("Подключение к базе данных для загрузки заказов...")
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='db_vgu_test'
            )

            with connection.cursor() as cursor:
                query = """
                SELECT 
                    zakazy.idZakaza,
                    zakazy.DataOformleniya, 
                    zakazy.DataVydachi, 
                    tovari.Naimenovanie,
                    zakazy.Kolichestvo, 
                    (zakazy.Kolichestvo * tovari.Tsenza) AS ИтоговаяЦена,
                    COALESCE(konditers.FIO, '-') AS КондитерФИО,
                    zakazchik.FIO AS ЗаказчикФИО,
                    statusyzakazov.StatusZakaza
                FROM zakazy
                LEFT JOIN konditers ON zakazy.Konditer = konditers.idKonditera
                JOIN statusyzakazov ON zakazy.Status = statusyzakazov.idStatusaZakaza
                JOIN sostavzakaza ON zakazy.idZakaza = sostavzakaza.Zakaz
                JOIN tovari ON sostavzakaza.Tovar = tovari.idTovara
                JOIN zakazchik ON zakazy.Zakazchik = zakazchik.idZakazchika
                WHERE statusyzakazov.StatusZakaza = 'v rabote'
                """
                cursor.execute(query)
                orders = cursor.fetchall()

            # Clear the table before loading data
            self.order_table.setRowCount(0)

            # Populate the table with data
            for row_idx, order in enumerate(orders):
                self.order_table.insertRow(row_idx)

                # Set order details in the specified order
                self.order_table.setItem(row_idx, 0, QTableWidgetItem(order[1].strftime("%Y-%m-%d")))
                self.order_table.setItem(row_idx, 1, QTableWidgetItem(order[2].strftime("%Y-%m-%d")))
                self.order_table.setItem(row_idx, 2, QTableWidgetItem(order[3]))
                self.order_table.setItem(row_idx, 3, QTableWidgetItem(str(order[4])))
                self.order_table.setItem(row_idx, 4, QTableWidgetItem(f"{order[5]:.2f}"))
                self.order_table.setItem(row_idx, 5, QTableWidgetItem(order[6]))
                self.order_table.setItem(row_idx, 6, QTableWidgetItem(order[7]))

                # Add a button to change the status
                status_button = QPushButton("✔️")
                status_button.setToolTip("Mark as completed")
                status_button.clicked.connect(lambda _, order_id=order[0]: self.mark_order_completed(order_id))
                self.order_table.setCellWidget(row_idx, 7, status_button)

            logging.info("Загрузка заказов завершена.")

        except pymysql.OperationalError as e:
            logging.error(f"Ошибка загрузки заказов: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка подключения к базе данных: {e}")

        except Exception as e:
            logging.error(f"Неизвестная ошибка: {e}")
            QMessageBox.critical(self, "Ошибка", f"Неизвестная ошибка: {e}")

        finally:
            if 'connection' in locals():
                connection.close()
                logging.info("Соединение закрыто после загрузки заказов.")

class PlaceOrderTab(QWidget):
    def __init__(self, order_tab):
        super().__init__()
        self.order_tab = order_tab  # Сохраняем ссылку на order_tab

        # Создаем основной вертикальный макет
        main_layout = QVBoxLayout()

        # Устанавливаем фиксированную ширину для полей ввода
        input_width = 300

        # Поле ввода ФИО заказчика
        self.customer_name_label = QLabel("ФИО заказчика:")
        self.customer_name_input = QLineEdit()
        self.customer_name_input.setFixedWidth(input_width)

        # Set a regular expression validator to allow only letters and spaces
        regex = QRegularExpression(r"^[А-Яа-яA-Za-z ]*$")
        validator = QRegularExpressionValidator(regex)
        self.customer_name_input.setValidator(validator)

        # Test the validator by connecting to the textChanged signal
        self.customer_name_input.textChanged.connect(self.validate_input)

        # Добавляем виджеты в основной макет
        main_layout.addWidget(self.customer_name_label)
        main_layout.addWidget(self.customer_name_input)

        # Устанавливаем основной макет для вкладки
        self.setLayout(main_layout)
        self.product_label = QLabel("Наименование товара:")
        self.product_combo = QComboBox()
        self.product_combo.setFixedWidth(input_width)
        self.load_products()
        self.product_combo.currentIndexChanged.connect(self.update_total_price)  # Connect signal

        # Поле ввода количества
        self.quantity_label = QLabel("Количество:")
        self.quantity_input = QLineEdit()
        self.quantity_input.setFixedWidth(input_width)
        self.quantity_input.textChanged.connect(self.update_total_price)


        # Поле ввода даты оформления
        self.order_date_label = QLabel("Дата оформления:")
        self.order_date_input = QLineEdit()
        self.order_date_input.setFixedWidth(input_width)
        self.order_date_input.setInputMask("00.00.0000")  # Set input mask for dd.mm.yyyy
        self.order_date_input.setText(datetime.now().strftime("%d.%m.%Y"))  # Set default to current date
        # Поле ввода даты выдачи
        self.delivery_date_label = QLabel("Дата выдачи:")
        self.delivery_date_input = QLineEdit()
        self.delivery_date_input.setFixedWidth(input_width)
        self.delivery_date_input.setInputMask("00.00.0000")  # Set input mask for dd.mm.yyyy
        self.delivery_date_input.setText(datetime.now().strftime("%d.%m.%Y"))  # Set default to current date

        # Выбор кондитера
        self.confectioner_label = QLabel("Кондитер:")
        self.confectioner_combo = QComboBox()
        self.confectioner_combo.setFixedWidth(input_width)
        self.load_confectioners()

        # Отображение итоговой цены
        self.total_price_label = QLabel("Итоговая цена:")
        self.total_price_display = QLabel("0.00")
        self.total_price_display.setFixedWidth(input_width)

        # Добавляем виджеты в основной макет
        main_layout.addWidget(self.customer_name_label)
        main_layout.addWidget(self.customer_name_input)
        main_layout.addWidget(self.product_label)
        main_layout.addWidget(self.product_combo)
        main_layout.addWidget(self.quantity_label)
        main_layout.addWidget(self.quantity_input)
        main_layout.addWidget(self.order_date_label)
        main_layout.addWidget(self.order_date_input)
        main_layout.addWidget(self.delivery_date_label)
        main_layout.addWidget(self.delivery_date_input)
        main_layout.addWidget(self.confectioner_label)
        main_layout.addWidget(self.confectioner_combo)
        main_layout.addWidget(self.total_price_label)
        main_layout.addWidget(self.total_price_display)

        # Создаем горизонтальный макет для кнопки
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # Добавляем растяжимое пространство слева

        # Увеличиваем размер кнопки и добавляем ее в макет
        self.place_order_button = QPushButton("Оформить")
        self.place_order_button.setFixedSize(170, 75)  # Устанавливаем размер кнопки
        self.place_order_button.clicked.connect(self.place_order)
        button_layout.addWidget(self.place_order_button)
        button_layout.addStretch()  # Добавляем растяжимое пространство справа

        # Добавляем макет кнопки в основной макет
        main_layout.addLayout(button_layout)

        # Добавляем растяжимое пространство для поднятия кнопки выше
        main_layout.addStretch()

        # Устанавливаем основной макет для вкладки
        self.setLayout(main_layout)
    def validate_input(self):
        state = self.customer_name_input.validator().validate(self.customer_name_input.text(), 0)
        if state[0] != QRegularExpressionValidator.State.Acceptable:
            print("Invalid input: Customer name cannot contain digits.")
    def load_statuses(self):
        """Loads statuses into the combo box."""
        self.status_combo.clear()

        try:
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='db_vgu_test'
            )

            with connection.cursor() as cursor:
                query = "SELECT idStatusaZakaza, StatusZakaza FROM statusyzakazov"
                cursor.execute(query)
                results = cursor.fetchall()

                for row in results:
                    self.status_combo.addItem(row[1], userData=row[0])

        except OperationalError as e:
            logging.error(f"Ошибка загрузки статусов: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки статусов: {e}")

        finally:
            if 'connection' in locals():
                connection.close()

    def load_products(self):
        """Loads products into the combo box."""
        try:
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='db_vgu_test'
            )

            with connection.cursor() as cursor:
                query = "SELECT idTovara, Naimenovanie, Tsenza FROM tovari"
                cursor.execute(query)
                results = cursor.fetchall()

                self.product_combo.clear()
                for row in results:
                    self.product_combo.addItem(f"{row[1]} ({row[2]} руб.)", userData=(row[0], row[2]))

        except OperationalError as e:
            logging.error(f"Ошибка загрузки товаров: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки товаров: {e}")

        finally:
            if 'connection' in locals():
                connection.close()

    def load_confectioners(self):
        """Loads confectioners into the combo box."""
        self.confectioner_combo.clear()

        try:
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='db_vgu_test'
            )

            with connection.cursor() as cursor:
                query = "SELECT idKonditera, FIO FROM konditers"
                cursor.execute(query)
                results = cursor.fetchall()

                for row in results:
                    self.confectioner_combo.addItem(row[1], userData=row[0])

        except OperationalError as e:
            logging.error(f"Ошибка загрузки кондитеров: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки кондитеров: {e}")

        finally:
            if 'connection' in locals():
                connection.close()

    def update_total_price(self):
        """Updates the total price based on the selected product and quantity."""
        try:
            product_data = self.product_combo.currentData()
            quantity = self.quantity_input.text().strip()

            if product_data and quantity.isdigit():
                price = product_data[1]
                total_price = int(quantity) * price
                self.total_price_display.setText(f"{total_price:.2f}")
            else:
                self.total_price_display.setText("0.00")
        except Exception as e:
            logging.error(f"Ошибка обновления итоговой цены: {e}")

    def place_order(self):
        """Places a new order in the database."""
        customer_name = self.customer_name_input.text().strip()
        product_data = self.product_combo.currentData()
        quantity = self.quantity_input.text().strip()
        order_date = self.order_date_input.text().strip()
        delivery_date = self.delivery_date_input.text().strip()
        confectioner_id = self.confectioner_combo.currentData()

        # Convert dates from dd.mm.yyyy to yyyy-mm-dd for database storage
        try:
            order_date_obj = datetime.strptime(order_date, "%d.%m.%Y")
            delivery_date_obj = datetime.strptime(delivery_date, "%d.%m.%Y")
        except ValueError:
            QMessageBox.warning(self, "Ошибка ввода", "Неверный формат даты. Используйте дд.мм.гггг.")
            return

        # Check if the delivery date is earlier than the order date
        if delivery_date_obj < order_date_obj:
            QMessageBox.warning(self, "Ошибка ввода", "Дата выдачи не может быть раньше даты оформления.")
            return

        # Determine the status based on whether a confectioner is selected
        status_id = 1 if confectioner_id else 2  # 1 for "Выдан", 2 for "Не выдан"

        if not customer_name:
            QMessageBox.warning(self, "Ошибка ввода", "Пожалуйста, введите ФИО заказчика.")
            return

        if not quantity.isdigit():
            QMessageBox.warning(self, "Ошибка ввода", "Количество должно быть числом.")
            return

        try:
            logging.info("Подключение к базе данных для оформления заказа...")
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='db_vgu_test'
            )

            with connection.cursor() as cursor:
                # Check available stock
                product_id = product_data[0]
                cursor.execute("SELECT Kolichestvo FROM tovari WHERE idTovara = %s", (product_id,))
                available_quantity = cursor.fetchone()[0]

                if int(quantity) > available_quantity:
                    QMessageBox.warning(self, "Ошибка", "Недостаточно товара на складе.")
                    return

                # Insert customer if not exists
                cursor.execute("SELECT idZakazchika FROM zakazchik WHERE FIO = %s", (customer_name,))
                customer = cursor.fetchone()
                if not customer:
                    cursor.execute("INSERT INTO zakazchik (FIO) VALUES (%s)", (customer_name,))
                    customer_id = cursor.lastrowid
                else:
                    customer_id = customer[0]

                # Insert order
                cursor.execute(
                    "INSERT INTO zakazy (DataOformleniya, DataVydachi, Kolichestvo, Konditer, Zakazchik, Status) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (order_date_obj.strftime("%Y-%m-%d"), delivery_date_obj.strftime("%Y-%m-%d"), quantity, confectioner_id, customer_id, status_id)
                )
                order_id = cursor.lastrowid

                # Insert order composition
                cursor.execute(
                    "INSERT INTO sostavzakaza (Tovar, Zakaz) VALUES (%s, %s)",
                    (product_id, order_id)
                )

                # Update stock quantity
                new_quantity = available_quantity - int(quantity)
                cursor.execute(
                    "UPDATE tovari SET Kolichestvo = %s WHERE idTovara = %s",
                    (new_quantity, product_id)
                )

                connection.commit()

            QMessageBox.information(self, "Успех", "Заказ успешно оформлен.")
            self.clear_inputs()

            # Refresh the orders tab and product list
            self.order_tab.load_orders()
            self.load_products()

        except OperationalError as e:
            logging.error(f"Ошибка оформления заказа: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка оформления заказа: {e}")

        except Exception as e:
            logging.error(f"Неизвестная ошибка: {e}")
            QMessageBox.critical(self, "Ошибка", f"Неизвестная ошибка: {e}")

        finally:
            if 'connection' in locals():
                connection.close()
                logging.info("Соединение закрыто после оформления заказа.")
    def clear_inputs(self):
        """Clears the input fields after placing an order and resets dates to the current date."""
        self.customer_name_input.clear()
        self.quantity_input.clear()
        self.total_price_display.setText("0.00")
        
        # Reset the order and delivery dates to today's date
        today_date = datetime.now().strftime("%d.%m.%Y")
        self.order_date_input.setText(today_date)
        self.delivery_date_input.setText(today_date)
class EditProductDialog(QDialog):
    def __init__(self, product_name, price, quantity, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать товар")

        # Store the original product name to identify the product in the database
        self.original_product_name = product_name

        # Create main layout
        main_layout = QVBoxLayout()

        # Name input
        self.name_label = QLabel("Наименование:")
        self.name_input = QLineEdit(product_name)
        self.name_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Price input
        self.price_label = QLabel("Цена:")
        self.price_input = QLineEdit(str(price))
        self.price_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Quantity input
        self.quantity_label = QLabel("Количество:")
        self.quantity_input = QLineEdit(str(quantity))
        self.quantity_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Add widgets to layout
        main_layout.addWidget(self.name_label)
        main_layout.addWidget(self.name_input)
        main_layout.addWidget(self.price_label)
        main_layout.addWidget(self.price_input)
        main_layout.addWidget(self.quantity_label)
        main_layout.addWidget(self.quantity_input)

        # Save button
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_product)
        main_layout.addWidget(self.save_button)

        # Set layout
        self.setLayout(main_layout)

    def save_product(self):
        """Saves the edited product details to the database."""
        new_name = self.name_input.text().strip()
        new_price = self.price_input.text().strip()
        new_quantity = self.quantity_input.text().strip()

        if not new_name:
            QMessageBox.warning(self, "Ошибка ввода", "Пожалуйста, введите наименование.")
            return

        if not new_price.isdigit():
            QMessageBox.warning(self, "Ошибка ввода", "Цена должна быть числом.")
            return

        if not new_quantity.isdigit():
            QMessageBox.warning(self, "Ошибка ввода", "Количество должно быть числом.")
            return

        try:
            logging.info("Подключение к базе данных для обновления товара...")
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='db_vgu_test'
            )

            with connection.cursor() as cursor:
                query = """
                UPDATE `tovari`
                SET `Naimenovanie` = %s, `Tsenza` = %s, `Kolichestvo` = %s
                WHERE `Naimenovanie` = %s
                """
                cursor.execute(query, (new_name, new_price, new_quantity, self.original_product_name))
                connection.commit()

            QMessageBox.information(self, "Успех", "Товар успешно обновлен.")
            self.accept()  # Close the dialog

        except OperationalError as e:
            logging.error(f"Ошибка обновления товара: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка обновления товара: {e}")

        finally:
            if 'connection' in locals():
                connection.close()
                logging.info("Соединение закрыто после обновления товара.")
class CompletedOrdersTab(QWidget):
    def __init__(self):
        super().__init__()

        # Create layout for the tab
        main_layout = QVBoxLayout()

        # Table to display completed orders
        self.completed_order_table = QTableWidget()
        self.completed_order_table.setColumnCount(8)
        self.completed_order_table.setHorizontalHeaderLabels([
            "Дата Оформления", "Дата Выдачи", "Наименование", "Количество", "Итоговая Цена", "Кондитер", "Заказчик", "Статус"
        ])
        self.completed_order_table.horizontalHeader().setStretchLastSection(True)
        self.completed_order_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.completed_order_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Connect double-click event
        self.completed_order_table.cellDoubleClicked.connect(self.open_delete_order_dialog)

        # Add table to main layout
        main_layout.addWidget(self.completed_order_table)
        self.completed_order_table.setColumnWidth(0, 150)
        # Set layout for the tab
        self.setLayout(main_layout)

        # Load completed orders from the database
        self.load_completed_orders()
    def open_delete_order_dialog(self, row, column):
        """Opens the dialog to confirm deletion of a completed order."""
        order_id = self.completed_order_table.item(row, 0).data(QtCore.Qt.ItemDataRole.UserRole)
        dialog = DeleteCompletedOrderDialog(order_id, self)
        if dialog.exec():
            self.load_completed_orders()
    def load_completed_orders(self):
        """Loads the completed orders from the database into the table."""
        try:
            logging.info("Подключение к базе данных для загрузки завершенных заказов...")
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='db_vgu_test'
            )

            with connection.cursor() as cursor:
                query = """
                SELECT 
                    zakazy.idZakaza,
                    zakazy.DataOformleniya, 
                    zakazy.DataVydachi, 
                    tovari.Naimenovanie,
                    zakazy.Kolichestvo, 
                    (zakazy.Kolichestvo * tovari.Tsenza) AS ИтоговаяЦена,
                    COALESCE(konditers.FIO, '-') AS КондитерФИО,
                    zakazchik.FIO AS ЗаказчикФИО,
                    statusyzakazov.StatusZakaza
                FROM zakazy
                LEFT JOIN konditers ON zakazy.Konditer = konditers.idKonditera
                JOIN statusyzakazov ON zakazy.Status = statusyzakazov.idStatusaZakaza
                JOIN sostavzakaza ON zakazy.idZakaza = sostavzakaza.Zakaz
                JOIN tovari ON sostavzakaza.Tovar = tovari.idTovara
                JOIN zakazchik ON zakazy.Zakazchik = zakazchik.idZakazchika
                WHERE zakazy.Status = 2
                """
                cursor.execute(query)
                completed_orders = cursor.fetchall()

            # Clear the table before loading data
            self.completed_order_table.setRowCount(0)

            # Populate the table with data
            for row_idx, order in enumerate(completed_orders):
                self.completed_order_table.insertRow(row_idx)

                # Store order ID as user data in the first column
                item = QTableWidgetItem(order[1].strftime("%Y-%m-%d"))
                item.setData(QtCore.Qt.ItemDataRole.UserRole, order[0])
                self.completed_order_table.setItem(row_idx, 0, item)

                self.completed_order_table.setItem(row_idx, 1, QTableWidgetItem(order[2].strftime("%Y-%m-%d")))
                self.completed_order_table.setItem(row_idx, 2, QTableWidgetItem(order[3]))
                self.completed_order_table.setItem(row_idx, 3, QTableWidgetItem(str(order[4])))
                self.completed_order_table.setItem(row_idx, 4, QTableWidgetItem(f"{order[5]:.2f}"))
                self.completed_order_table.setItem(row_idx, 5, QTableWidgetItem(order[6]))
                self.completed_order_table.setItem(row_idx, 6, QTableWidgetItem(order[7]))

                # Add a cross icon to indicate completion
                status_label = QLabel("❌")
                status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.completed_order_table.setCellWidget(row_idx, 7, status_label)

            logging.info("Загрузка завершенных заказов завершена.")

        except pymysql.OperationalError as e:
            logging.error(f"Ошибка загрузки завершенных заказов: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка подключения к базе данных: {e}")

        except Exception as e:
            logging.error(f"Неизвестная ошибка: {e}")
            QMessageBox.critical(self, "Ошибка", f"Неизвестная ошибка: {e}")

        finally:
            if 'connection' in locals():
                connection.close()
                logging.info("Соединение закрыто после загрузки завершенных заказов.")
class DeleteCompletedOrderDialog(QDialog):
    def __init__(self, order_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Удалить завершенный заказ")
        self.order_id = order_id

        # Create main layout
        main_layout = QVBoxLayout()

        # Confirmation message
        self.confirm_label = QLabel("Вы уверены, что хотите удалить этот завершенный заказ?")
        main_layout.addWidget(self.confirm_label)

        # Delete button
        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_order)
        main_layout.addWidget(self.delete_button)

        # Set layout
        self.setLayout(main_layout)

    def delete_order(self):
        """Deletes the completed order from the database."""
        try:
            connection = pymysql.connect(
                host='5.183.188.132',
                user=db_user,
                password=db_password,
                database='db_vgu_test'
            )

            with connection.cursor() as cursor:
                # First, delete related records in the `sostavzakaza` table
                query = "DELETE FROM sostavzakaza WHERE Zakaz = %s"
                cursor.execute(query, (self.order_id,))

                # Now, delete the order itself
                query = "DELETE FROM zakazy WHERE idZakaza = %s"
                cursor.execute(query, (self.order_id,))
                connection.commit()

            QMessageBox.information(self, "Успех", "Завершенный заказ успешно удален.")
            self.accept()  # Close the dialog

        except OperationalError as e:
            logging.error(f"Ошибка удаления завершенного заказа: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка удаления завершенного заказа: {e}")

        finally:
            if 'connection' in locals():
                connection.close()
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Менеджер компании")

        # Use the custom tab widget
        self.tabs = VerticalQTabWidget()

        # Create tabs with the role 'Админ'
        self.confectioner_tab = ConfectionerTab(role="Админ")
        self.completed_orders_tab = CompletedOrdersTab()
        self.order_tab = OrderTab(self.completed_orders_tab, None, "Админ")  # Pass role as "Админ"
        self.place_order_tab = PlaceOrderTab(self.order_tab)
        self.Product_tab = ProductTab()

        # Add tabs to the tab widget
        self.tabs.addTab(self.confectioner_tab, "Кондитеры")
        self.tabs.addTab(self.order_tab, "Текущие заказы")
        self.tabs.addTab(self.completed_orders_tab, "Завершенные заказы")
        self.tabs.addTab(self.place_order_tab, "Оформить заказ")
        self.tabs.addTab(self.Product_tab, "Товары")

        # Set the central widget
        self.setCentralWidget(self.tabs)
class WelcomeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добро пожаловать")
        self.role = None
        self.confectioner_id = None  # Initialize the confectioner_id attribute

        # Set a larger size for the dialog
        self.setMinimumSize(800, 600)

        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)

        # Add a label for the title
        self.title_label = QLabel("Учет заказов на кондитерской фабрике")
        self.title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-top: 200px;")
        main_layout.addWidget(self.title_label)

        # Add a button for entering
        self.enter_button = QPushButton("Вход")
        self.enter_button.setFixedSize(150, 50)
        self.enter_button.clicked.connect(self.open_login_dialog)
        main_layout.addWidget(self.enter_button, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        # Set layout for the dialog
        self.setLayout(main_layout)

        # Apply custom styles
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f8ff;
                border-radius: 10px;
                padding: 20px;
            }
            QLabel {
                font-size: 18px;
                color: #333333;
            }
            QPushButton {
                background-color: #FF69B4;
                border: 1px solid #a0a0a0;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #dda0dd;
            }
        """)

    def open_login_dialog(self):
        """Open the login dialog when the button is clicked."""
        login_dialog = LoginDialog(self)
        if login_dialog.exec() == QDialog.DialogCode.Accepted:
            self.role = login_dialog.role
            self.confectioner_id = login_dialog.confectioner_id  # Store the confectioner_id
            self.accept()
def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    welcome_dialog = WelcomeDialog()
    if welcome_dialog.exec() == QDialog.DialogCode.Accepted:
        role = welcome_dialog.role
        confectioner_id = welcome_dialog.confectioner_id

        if role == "Админ":
            window = MainWindow()
        else:
            window = ConfectionerWindow(confectioner_id)

        # Apply a custom stylesheet with reversed soft blue and soft purple colors
        app.setStyleSheet("""
            QMainWindow {
                background-color: #f0f8ff;  /* Alice blue background */
            }
            QTabWidget::pane {
                border: 1px solid #b0b0b0;
                background-color: #FFFACD;  /* Soft lavender background */
            }
            QTabBar::tab {
                background: #b0c4de;  /* Light steel blue */
                border: 1px solid #b0b0b0;
                padding: 12px;
                margin: 3px;
                border-radius: 5px;
                font-size: 14px;
            }
            QTabBar::tab:selected {
                background: #FFC0CB;  /* Thistle color */
                font-weight: bold;
                color: #ffffff;
            }
            QTabBar::tab:hover {
                background: #dda0dd;  /* Plum color */
            }
            QPushButton {
                background-color: #FF69B4;  /* Thistle color */
                border: 1px solid #a0a0a0;
                padding: 6px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #dda0dd;  /* Plum color */
            }
            QLabel {
                font-size: 15px;
                color: #333333;
            }
            QLineEdit, QComboBox {
                border: 1px solid #a0a0a0;
                padding: 6px;
                border-radius: 4px;
                background-color: #e6e6fa;  /* Soft lavender */
            }
            QTableWidget {
                gridline-color: #b0b0b0;
                background-color: #ffffff;
            }
            QHeaderView::section {
                background-color: #d8bfd8;  /* Thistle color */
                border: 1px solid #a0a0a0;
                padding: 6px;
                font-weight: bold;
            }
        """)
        
        window.showMaximized()
        sys.exit(app.exec())

if __name__ == "__main__":
    main()