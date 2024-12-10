import sys
import logging
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QComboBox,QDialog, QHBoxLayout,QSizePolicy,
    QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QTabWidget, QTabBar, QStylePainter, QStyleOptionTab, QStyleOptionTabWidgetFrame, QStyle
)
import pymysql
from pymysql import OperationalError
from PyQt6 import QtCore
logging.basicConfig(level=logging.INFO)
db_user = "Aimor"
db_password = "Alex25122005"


class VerticalQTabWidget(QTabWidget):
    def __init__(self):
        super(VerticalQTabWidget, self).__init__()
        self.setTabBar(VerticalQTabBar())
        self.setTabPosition(QTabWidget.TabPosition.West)

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
class AddConfectionerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить кондитера")

        # Create main vertical layout for the dialog
        main_layout = QVBoxLayout()

        # Create a horizontal layout for the name and experience
        input_layout = QHBoxLayout()
        
        # Create a grid layout to align labels and inputs
        grid_layout = QVBoxLayout()
        
        # Name input
        self.name_label = QLabel("ФИО:")
        self.name_input = QLineEdit()
        self.name_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Experience input
        self.experience_label = QLabel("Стаж:")
        self.experience_input = QLineEdit()
        self.experience_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Add widgets to grid layout
        grid_layout.addWidget(self.name_label)
        grid_layout.addWidget(self.name_input)
        grid_layout.addWidget(self.experience_label)
        grid_layout.addWidget(self.experience_input)
        
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

    def add_confectioner(self):
        """Adds a new confectioner to the database."""
        name = self.name_input.text().strip()
        experience = self.experience_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Ошибка ввода", "Пожалуйста, введите ФИО.")
            return

        if not experience.isdigit():
            QMessageBox.warning(self, "Ошибка ввода", "Стаж должен быть числом.")
            return

        try:
            logging.info("Подключение к базе данных для добавления кондитера...")
            connection = pymysql.connect(
                host='127.0.0.1',
                user=db_user,
                password=db_password,
                database='Kond'
            )

            with connection.cursor() as cursor:
                query = "INSERT INTO `Кондитеры` (`ФИО`, `Стаж`) VALUES (%s, %s)"
                cursor.execute(query, (name, experience))
                connection.commit()

            QMessageBox.information(self, "Успех", "Кондитер успешно добавлен.")
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
                host='127.0.0.1', 
                user=db_user, 
                password=db_password, 
                database='Kond' 
            ) 
 
            with connection.cursor() as cursor: 
                query = "SELECT idКондитера, ФИО FROM Кондитеры" 
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
                    host='127.0.0.1', 
                    user=db_user, 
                    password=db_password, 
                    database='Kond' 
                ) 
 
                with connection.cursor() as cursor: 
                    query = "DELETE FROM Кондитеры WHERE idКондитера = %s" 
                    cursor.execute(query, (confectioner_id,)) 
                    connection.commit() 
 
                QMessageBox.information(self, "Успех", "Кондитер успешно удален.") 
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

class ConfectionerTab(QWidget):
    def __init__(self):
        super().__init__()

        # Create layout for the tab
        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        # Table to display confectioners
        self.confectioner_table = QTableWidget()
        self.confectioner_table.setColumnCount(2)  # Remove ID
        self.confectioner_table.setHorizontalHeaderLabels(["ФИО", "Стаж"])

        # Buttons for adding and deleting confectioners
        self.add_button = QPushButton("Добавить кондитера")
        self.add_button.clicked.connect(self.show_add_confectioner_dialog)

        self.delete_button = QPushButton("Удалить кондитера")
        self.delete_button.clicked.connect(self.show_delete_confectioner_dialog)

        # Add buttons to button layout
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)

        # Add widgets to main layout
        main_layout.addWidget(self.confectioner_table)
        main_layout.addLayout(button_layout)

        # Set layout for the tab
        self.setLayout(main_layout)

        # Load data
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
                host='127.0.0.1',
                user=db_user,
                password=db_password,
                database='Kond'
            )

            with connection.cursor() as cursor:
                query = "SELECT `ФИО`, `Стаж` FROM `Кондитеры`"
                cursor.execute(query)
                results = cursor.fetchall()

                self.confectioner_table.setRowCount(len(results))
                for row_index, row_data in enumerate(results):
                    self.confectioner_table.setItem(row_index, 0, QTableWidgetItem(row_data[0]))
                    self.confectioner_table.setItem(row_index, 1, QTableWidgetItem(str(row_data[1])))

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
                    host='127.0.0.1',
                    user=db_user,
                    password=db_password,
                    database='Kond'
                )

                with connection.cursor() as cursor:
                    query = "DELETE FROM `Кондитеры` WHERE `ФИО` = %s"
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
                host='127.0.0.1',
                user=db_user,
                password=db_password,
                database='Kond'
            )

            with connection.cursor() as cursor:
                query = "INSERT INTO `Товары` (`Наименование`, `Цена`, `Количество`) VALUES (%s, %s, %s)"
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

        # Create layout for the tab
        main_layout = QVBoxLayout()

        # Table to display products
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(4)  # Наименование, Цена, Количество, Удалить
        self.product_table.setHorizontalHeaderLabels(["Наименование", "Цена", "Количество", "Удалить"])
        self.product_table.horizontalHeader().setStretchLastSection(True)
        self.product_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.product_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Add table to main layout
        main_layout.addWidget(self.product_table)

        # Button to add a product
        self.add_product_button = QPushButton("Добавить товар")
        self.add_product_button.clicked.connect(self.open_add_product_dialog)

        # Add button to main layout
        main_layout.addWidget(self.add_product_button)

        # Set layout for the tab
        self.setLayout(main_layout)

        # Load products from the database
        self.load_products()

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
                host='127.0.0.1',
                user=db_user,
                password=db_password,
                database='Kond'
            )

            with connection.cursor() as cursor:
                query = "SELECT `Наименование`, `Цена`, `Количество` FROM `Товары`"
                cursor.execute(query)
                products = cursor.fetchall()

            # Очистка таблицы перед загрузкой данных
            self.product_table.setRowCount(0)

            # Заполнение таблицы данными
            for row_idx, product in enumerate(products):
                self.product_table.insertRow(row_idx)

                # Установить наименование
                self.product_table.setItem(row_idx, 0, QTableWidgetItem(product[0]))

                # Установить цену
                self.product_table.setItem(row_idx, 1, QTableWidgetItem(str(product[1])))
                self.product_table.setItem(row_idx, 2, QTableWidgetItem(str(product[2]))) 

                # Добавить кнопку удаления
                delete_button = QPushButton("❌")
                delete_button.setToolTip(f"Удалить {product[0]}")
                delete_button.clicked.connect(self._create_delete_handler(product[0]))
                self.product_table.setCellWidget(row_idx, 3, delete_button)

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

    def _create_delete_handler(self, product_name):
        """Создает обработчик для удаления конкретного товара."""
        def delete_product():
            confirm = QMessageBox.question(
                self,
                "Подтверждение",
                f"Вы уверены, что хотите удалить товар '{product_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if confirm == QMessageBox.StandardButton.Yes:
                try:
                    logging.info(f"Удаление товара '{product_name}' из базы данных...")
                    connection = pymysql.connect(
                        host='127.0.0.1',
                        user=db_user,
                        password=db_password,
                        database='Kond'
                    )

                    with connection.cursor() as cursor:
                        query = "DELETE FROM `Товары` WHERE `Наименование` = %s"
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



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Менеджер компании")

        # Используем кастомный виджет вкладок
        self.tabs = VerticalQTabWidget()

        # Создаем вкладки
        self.confectioner_tab = ConfectionerTab()
        # Добавьте другие вкладки, если они есть
        self.product_tab = ProductTab()
        # self.sales_tab = SalesTab()

        self.tabs.addTab(self.confectioner_tab, "Кондитеры")
        # Добавьте другие вкладки, если они есть
        self.tabs.addTab(self.product_tab, "Товары")
        # self.tabs.addTab(self.sales_tab, "Продажи")

        # Устанавливаем центральный виджет
        self.setCentralWidget(self.tabs)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()  # Открываем приложение на весь экран
    sys.exit(app.exec())

if __name__ == "__main__":
    main()