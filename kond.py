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

        # Create a horizontal layout for the name, experience, and status
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
                host='127.0.0.1',
                user=db_user,
                password=db_password,
                database='Kond'
            )

            with connection.cursor() as cursor:
                query = "SELECT idСтатуса, Статус FROM Статусы"
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

        try:
            logging.info("Подключение к базе данных для добавления кондитера...")
            connection = pymysql.connect(
                host='127.0.0.1',
                user=db_user,
                password=db_password,
                database='Kond'
            )

            with connection.cursor() as cursor:
                query = "INSERT INTO `Кондитеры` (`ФИО`, `Стаж`, `Статус`) VALUES (%s, %s, %s)"
                cursor.execute(query, (name, experience, status_id))
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
        self.confectioner_table.setColumnCount(3)  # Add column for status
        self.confectioner_table.setHorizontalHeaderLabels(["ФИО", "Стаж", "Статус"])

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
                query = """
                SELECT Кондитеры.ФИО, Кондитеры.Стаж, Статусы.статус
                FROM Кондитеры
                JOIN Статусы ON Кондитеры.Статус = idСтатуса
                """
                cursor.execute(query)
                results = cursor.fetchall()

                self.confectioner_table.setRowCount(len(results))
                for row_index, row_data in enumerate(results):
                    self.confectioner_table.setItem(row_index, 0, QTableWidgetItem(row_data[0]))
                    self.confectioner_table.setItem(row_index, 1, QTableWidgetItem(str(row_data[1])))
                    self.confectioner_table.setItem(row_index, 2, QTableWidgetItem(row_data[2]))

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

class OrderTab(QWidget):
    def __init__(self):
        super().__init__()

        # Create layout for the tab
        main_layout = QVBoxLayout()

        # Table to display orders
        self.order_table = QTableWidget()
        self.order_table.setColumnCount(8)  # Updated column count
        self.order_table.setHorizontalHeaderLabels([
            "Дата Оформления", "Дата Выдачи", "Наименование", "Количество", "Итоговая Цена", "Кондитер", "Заказчик", "Статус"
        ])
        self.order_table.horizontalHeader().setStretchLastSection(True)
        self.order_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.order_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Add table to main layout
        main_layout.addWidget(self.order_table)

        # Set layout for the tab
        self.setLayout(main_layout)

        # Load orders from the database
        self.load_orders()

    def load_orders(self):
        """Loads the orders from the database into the table."""
        try:
            logging.info("Подключение к базе данных для загрузки заказов...")
            connection = pymysql.connect(
                host='127.0.0.1',
                user=db_user,
                password=db_password,
                database='Kond'
            )

            with connection.cursor() as cursor:
                query = """
                SELECT 
                    заказы.ДатаОформления, 
                    заказы.ДатаВыдачи, 
                    Товары.Наименование,
                    заказы.Количество, 
                    (заказы.Количество * Товары.Цена) AS ИтоговаяЦена,
                    COALESCE(Кондитеры.ФИО, '-') AS КондитерФИО,
                    Заказчик.ФИО AS ЗаказчикФИО,
                    СтатусыЗаказов.СтатусЗаказа
                FROM заказы
                LEFT JOIN Кондитеры ON заказы.Кондитер = Кондитеры.idКондитера
                JOIN СтатусыЗаказов ON заказы.Статус = СтатусыЗаказов.idСтатусаЗаказа
                JOIN составзаказа ON заказы.idЗаказа = составзаказа.Заказ
                JOIN Товары ON составзаказа.Товар = Товары.idТовара
                JOIN Заказчик ON заказы.Заказчик = Заказчик.idЗаказчика
                """
                cursor.execute(query)
                orders = cursor.fetchall()

            # Clear the table before loading data
            self.order_table.setRowCount(0)

            # Populate the table with data
            for row_idx, order in enumerate(orders):
                self.order_table.insertRow(row_idx)

                # Set order details in the specified order
                self.order_table.setItem(row_idx, 0, QTableWidgetItem(order[0].strftime("%Y-%m-%d")))
                self.order_table.setItem(row_idx, 1, QTableWidgetItem(order[1].strftime("%Y-%m-%d")))
                self.order_table.setItem(row_idx, 2, QTableWidgetItem(order[2]))
                self.order_table.setItem(row_idx, 3, QTableWidgetItem(str(order[3])))
                self.order_table.setItem(row_idx, 4, QTableWidgetItem(f"{order[4]:.2f}"))
                self.order_table.setItem(row_idx, 5, QTableWidgetItem(order[5]))
                self.order_table.setItem(row_idx, 6, QTableWidgetItem(order[6]))

                # Set status with checkmark or cross
                status_item = QTableWidgetItem("✔️" if order[7] == "В работе" else "❌" )
                status_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.order_table.setItem(row_idx, 7, status_item)

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
        self.order_tab = order_tab  # Store the reference to order_tab

        # Create layout for the tab
        main_layout = QVBoxLayout()

        # Customer name input
        self.customer_name_label = QLabel("ФИО заказчика:")
        self.customer_name_input = QLineEdit()
        self.customer_name_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Product selection
        self.product_label = QLabel("Наименование товара:")
        self.product_combo = QComboBox()
        self.load_products()

        # Quantity input
        self.quantity_label = QLabel("Количество:")
        self.quantity_input = QLineEdit()
        self.quantity_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.quantity_input.textChanged.connect(self.update_total_price)

        # Order date input
        self.order_date_label = QLabel("Дата оформления:")
        self.order_date_input = QLineEdit()
        self.order_date_input.setPlaceholderText("YYYY-MM-DD")

        # Delivery date input
        self.delivery_date_label = QLabel("Дата выдачи:")
        self.delivery_date_input = QLineEdit()
        self.delivery_date_input.setPlaceholderText("YYYY-MM-DD")

        # Confectioner selection
        self.confectioner_label = QLabel("Кондитер:")
        self.confectioner_combo = QComboBox()
        self.load_confectioners()

        # Total price display
        self.total_price_label = QLabel("Итоговая цена:")
        self.total_price_display = QLabel("0.00")

        # Button to place order
        self.place_order_button = QPushButton("Оформить")
        self.place_order_button.clicked.connect(self.place_order)

        # Add widgets to layout
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
        main_layout.addWidget(self.place_order_button)

        # Set layout for the tab
        self.setLayout(main_layout)
    def load_statuses(self):
        """Loads statuses into the combo box."""
        self.status_combo.clear()
        self.status_combo.addItem("-", userData=None)  # Default option for undelivered orders

        try:
            connection = pymysql.connect(
                host='127.0.0.1',
                user=db_user,
                password=db_password,
                database='Kond'
            )

            with connection.cursor() as cursor:
                query = "SELECT idСтатусаЗаказа, СтатусЗаказа FROM СтатусыЗаказов"
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
                host='127.0.0.1',
                user=db_user,
                password=db_password,
                database='Kond'
            )

            with connection.cursor() as cursor:
                query = "SELECT idТовара, Наименование, Цена FROM Товары"
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
        self.confectioner_combo.addItem("-", userData=None)  # Default option for unassigned orders

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

        # Determine the status based on whether a confectioner is selected
        status_id = 1 if confectioner_id else 2  # 1 for "Выдан", 2 for "Не выдан"

        if not customer_name:
            QMessageBox.warning(self, "Ошибка ввода", "Пожалуйста, введите ФИО заказчика.")
            return

        if not quantity.isdigit():
            QMessageBox.warning(self, "Ошибка ввода", "Количество должно быть числом.")
            return

        if not order_date or not delivery_date:
            QMessageBox.warning(self, "Ошибка ввода", "Пожалуйста, введите даты оформления и выдачи.")
            return

        try:
            logging.info("Подключение к базе данных для оформления заказа...")
            connection = pymysql.connect(
                host='127.0.0.1',
                user=db_user,
                password=db_password,
                database='Kond'
            )

            with connection.cursor() as cursor:
                # Insert customer if not exists
                cursor.execute("SELECT idЗаказчика FROM Заказчик WHERE ФИО = %s", (customer_name,))
                customer = cursor.fetchone()
                if not customer:
                    cursor.execute("INSERT INTO Заказчик (ФИО) VALUES (%s)", (customer_name,))
                    customer_id = cursor.lastrowid
                else:
                    customer_id = customer[0]

                # Insert order
                cursor.execute(
                    "INSERT INTO заказы (ДатаОформления, ДатаВыдачи, Количество, Кондитер, Заказчик, Статус) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (order_date, delivery_date, quantity, confectioner_id, customer_id, status_id)
                )
                order_id = cursor.lastrowid

                # Insert order composition
                cursor.execute(
                    "INSERT INTO составзаказа (Товар, Заказ) VALUES (%s, %s)",
                    (product_data[0], order_id)
                )

                connection.commit()

            QMessageBox.information(self, "Успех", "Заказ успешно оформлен.")
            self.clear_inputs()

            # Refresh the orders tab
            self.order_tab.load_orders()

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
        """Clears the input fields after placing an order."""
        self.customer_name_input.clear()
        self.quantity_input.clear()
        self.order_date_input.clear()
        self.delivery_date_input.clear()
        self.total_price_display.setText("0.00")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Менеджер компании")

        # Используем пользовательский виджет вкладок
        self.tabs = VerticalQTabWidget()

        # Создаем вкладки
        self.confectioner_tab = ConfectionerTab()
        self.product_tab = ProductTab()
        self.order_tab = OrderTab()
        self.place_order_tab = PlaceOrderTab(self.order_tab)  # Передаем order_tab в PlaceOrderTab

        # Добавляем вкладки в виджет вкладок
        self.tabs.addTab(self.confectioner_tab, "Кондитеры")
        self.tabs.addTab(self.product_tab, "Товары")
        self.tabs.addTab(self.order_tab, "Текущие заказы")
        self.tabs.addTab(self.place_order_tab, "Оформить заказ")

        # Устанавливаем центральный виджет
        self.setCentralWidget(self.tabs)


def main():
    app = QApplication(sys.argv)
    
    # Set the application style to 'Fusion'
    app.setStyle('Fusion')

    # Apply a custom stylesheet
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f5f5;
        }
        QTabWidget::pane {
            border: 1px solid #b0b0b0;
            background-color: #ffffff;
        }
        QTabBar::tab {
            background: #e8e8e8;
            border: 1px solid #b0b0b0;
            padding: 12px;
            margin: 3px;
            border-radius: 5px;
            font-size: 14px;
        }
        QTabBar::tab:selected {
            background: #d0d0d0;
            font-weight: bold;
            color: #333333;
        }
        QTabBar::tab:hover {
            background: #c8c8c8;
        }
        QPushButton {
            background-color: #d0d0d0;
            border: 1px solid #a0a0a0;
            padding: 6px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #c0c0c0;
        }
        QLabel {
            font-size: 15px;
            color: #333333;
        }
        QLineEdit, QComboBox {
            border: 1px solid #a0a0a0;
            padding: 6px;
            border-radius: 4px;
        }
        QTableWidget {
            gridline-color: #b0b0b0;
            background-color: #ffffff;
        }
        QHeaderView::section {
            background-color: #d0d0d0;
            border: 1px solid #a0a0a0;
            padding: 6px;
            font-weight: bold;
        }
    """)

    window = MainWindow()
    window.showMaximized()  # Open the application in full screen
    sys.exit(app.exec())

if __name__ == "__main__":
    main()