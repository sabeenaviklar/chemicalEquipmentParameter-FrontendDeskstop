import sys
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                             QFileDialog, QTableWidget, QTableWidgetItem, 
                             QTabWidget, QMessageBox, QListWidget, QGroupBox,
                             QGridLayout, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd

API_BASE_URL = 'http://127.0.0.1:8000/api'

class LoginWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Login - Chemical Equipment Visualizer')
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Title
        title = QLabel('Chemical Equipment Visualizer')
        title.setFont(QFont('Arial', 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Username
        username_label = QLabel('Username:')
        self.username_input = QLineEdit()
        layout.addWidget(username_label)
        layout.addWidget(self.username_input)
        
        # Password
        password_label = QLabel('Password:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        login_btn = QPushButton('Login')
        login_btn.clicked.connect(self.login)
        login_btn.setStyleSheet("background-color: #667eea; color: white; padding: 10px;")
        
        register_btn = QPushButton('Register')
        register_btn.clicked.connect(self.register)
        register_btn.setStyleSheet("background-color: #764ba2; color: white; padding: 10px;")
        
        button_layout.addWidget(login_btn)
        button_layout.addWidget(register_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, 'Error', 'Please enter username and password')
            return
        
        try:
            response = requests.post(f'{API_BASE_URL}/login/', json={
                'username': username,
                'password': password
            })
            
            if response.status_code == 200:
                data = response.json()
                self.main_window.set_token(data['token'])
                self.main_window.show()
                self.close()
            else:
                QMessageBox.warning(self, 'Error', 'Invalid credentials')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Login failed: {str(e)}')
    
    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, 'Error', 'Please enter username and password')
            return
        
        try:
            response = requests.post(f'{API_BASE_URL}/register/', json={
                'username': username,
                'password': password,
                'email': ''
            })
            
            if response.status_code == 201:
                data = response.json()
                self.main_window.set_token(data['token'])
                self.main_window.show()
                self.close()
            else:
                error = response.json().get('error', 'Registration failed')
                QMessageBox.warning(self, 'Error', error)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Registration failed: {str(e)}')


class ChartCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(figsize=(6, 4))
        self.axes = fig.add_subplot(111)
        super().__init__(fig)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.token = None
        self.current_dataset_id = None
        self.init_ui()
    
    def set_token(self, token):
        self.token = token
    
    def init_ui(self):
        self.setWindowTitle('Chemical Equipment Visualizer - Desktop')
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title
        title = QLabel('⚗️ Chemical Equipment Visualizer')
        title.setFont(QFont('Arial', 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #667eea; padding: 10px;")
        main_layout.addWidget(title)
        
        # Create tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Create tabs
        self.upload_tab = self.create_upload_tab()
        self.history_tab = self.create_history_tab()
        
        self.tabs.addTab(self.upload_tab, "📤 Upload")
        self.tabs.addTab(self.history_tab, "📜 History")
    
    def create_upload_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Upload section
        upload_group = QGroupBox("Upload CSV File")
        upload_layout = QVBoxLayout()
        
        self.file_label = QLabel('No file selected')
        self.file_label.setAlignment(Qt.AlignCenter)
        self.file_label.setStyleSheet("padding: 20px; border: 2px dashed #667eea; border-radius: 10px;")
        upload_layout.addWidget(self.file_label)
        
        button_layout = QHBoxLayout()
        select_btn = QPushButton('Select CSV File')
        select_btn.clicked.connect(self.select_file)
        select_btn.setStyleSheet("background-color: #667eea; color: white; padding: 10px;")
        
        upload_btn = QPushButton('Upload')
        upload_btn.clicked.connect(self.upload_file)
        upload_btn.setStyleSheet("background-color: #764ba2; color: white; padding: 10px;")
        
        button_layout.addWidget(select_btn)
        button_layout.addWidget(upload_btn)
        upload_layout.addLayout(button_layout)
        
        upload_group.setLayout(upload_layout)
        layout.addWidget(upload_group)
        
        # Statistics section
        stats_group = QGroupBox("Summary Statistics")
        stats_layout = QGridLayout()
        
        self.total_label = QLabel('Total: -')
        self.flowrate_label = QLabel('Avg Flowrate: -')
        self.pressure_label = QLabel('Avg Pressure: -')
        self.temp_label = QLabel('Avg Temperature: -')
        
        for label in [self.total_label, self.flowrate_label, self.pressure_label, self.temp_label]:
            label.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:1 #764ba2); color: white; padding: 15px; border-radius: 10px; font-size: 14px;")
        
        stats_layout.addWidget(self.total_label, 0, 0)
        stats_layout.addWidget(self.flowrate_label, 0, 1)
        stats_layout.addWidget(self.pressure_label, 0, 2)
        stats_layout.addWidget(self.temp_label, 0, 3)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Charts section
        charts_group = QGroupBox("Visualizations")
        charts_layout = QHBoxLayout()
        
        self.pie_chart = ChartCanvas()
        self.bar_chart = ChartCanvas()
        
        charts_layout.addWidget(self.pie_chart)
        charts_layout.addWidget(self.bar_chart)
        
        charts_group.setLayout(charts_layout)
        layout.addWidget(charts_group)
        
        # Data table
        table_group = QGroupBox("Equipment Data")
        table_layout = QVBoxLayout()
        
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(5)
        self.data_table.setHorizontalHeaderLabels(['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'])
        table_layout.addWidget(self.data_table)
        
        # Download PDF button
        pdf_btn = QPushButton('📥 Download PDF Report')
        pdf_btn.clicked.connect(self.download_pdf)
        pdf_btn.setStyleSheet("background-color: #4caf50; color: white; padding: 10px;")
        table_layout.addWidget(pdf_btn)
        
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_history_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel('Upload History (Last 5)')
        title.setFont(QFont('Arial', 14, QFont.Bold))
        layout.addWidget(title)
        
        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self.load_dataset_from_history)
        layout.addWidget(self.history_list)
        
        refresh_btn = QPushButton('🔄 Refresh History')
        refresh_btn.clicked.connect(self.load_history)
        refresh_btn.setStyleSheet("background-color: #667eea; color: white; padding: 10px;")
        layout.addWidget(refresh_btn)
        
        tab.setLayout(layout)
        return tab
    
    def select_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Select CSV File', '', 'CSV Files (*.csv)')
        if filename:
            self.selected_file = filename
            self.file_label.setText(f'Selected: {filename.split("/")[-1]}')
    
    def upload_file(self):
        if not hasattr(self, 'selected_file'):
            QMessageBox.warning(self, 'Error', 'Please select a file first')
            return
        
        try:
            with open(self.selected_file, 'rb') as f:
                files = {'file': f}
                headers = {'Authorization': f'Token {self.token}'} if self.token else {}
                
                response = requests.post(f'{API_BASE_URL}/upload/', files=files, headers=headers)
                
                if response.status_code == 201:
                    data = response.json()
                    QMessageBox.information(self, 'Success', f'File uploaded successfully! {data["record_count"]} records added.')
                    self.current_dataset_id = data['dataset_id']
                    self.load_dataset(data['dataset_id'])
                else:
                    error = response.json().get('error', 'Upload failed')
                    QMessageBox.warning(self, 'Error', error)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Upload failed: {str(e)}')
    
    def load_dataset(self, dataset_id):
        try:
            headers = {'Authorization': f'Token {self.token}'} if self.token else {}
            
            # Get dataset details
            detail_response = requests.get(f'{API_BASE_URL}/datasets/{dataset_id}/', headers=headers)
            summary_response = requests.get(f'{API_BASE_URL}/datasets/{dataset_id}/summary/', headers=headers)
            
            if detail_response.status_code == 200 and summary_response.status_code == 200:
                detail_data = detail_response.json()
                summary_data = summary_response.json()
                
                # Update statistics
                self.total_label.setText(f"Total Equipment: {summary_data['total_count']}")
                self.flowrate_label.setText(f"Avg Flowrate: {summary_data['averages']['flowrate']:.2f}")
                self.pressure_label.setText(f"Avg Pressure: {summary_data['averages']['pressure']:.2f}")
                self.temp_label.setText(f"Avg Temperature: {summary_data['averages']['temperature']:.2f}")
                
                # Update table
                equipment = detail_data['equipment']
                self.data_table.setRowCount(len(equipment))
                
                for i, item in enumerate(equipment):
                    self.data_table.setItem(i, 0, QTableWidgetItem(item['equipment_name']))
                    self.data_table.setItem(i, 1, QTableWidgetItem(item['type']))
                    self.data_table.setItem(i, 2, QTableWidgetItem(f"{item['flowrate']:.2f}"))
                    self.data_table.setItem(i, 3, QTableWidgetItem(f"{item['pressure']:.2f}"))
                    self.data_table.setItem(i, 4, QTableWidgetItem(f"{item['temperature']:.2f}"))
                
                # Update charts
                self.update_charts(summary_data['type_distribution'], summary_data['averages'])
                
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to load dataset: {str(e)}')
    
    def update_charts(self, type_distribution, averages):
        # Pie chart
        self.pie_chart.axes.clear()
        labels = list(type_distribution.keys())
        sizes = list(type_distribution.values())
        self.pie_chart.axes.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        self.pie_chart.axes.set_title('Equipment Type Distribution')
        self.pie_chart.draw()
        
        # Bar chart
        self.bar_chart.axes.clear()
        params = ['Flowrate', 'Pressure', 'Temperature']
        values = [averages['flowrate'], averages['pressure'], averages['temperature']]
        self.bar_chart.axes.bar(params, values, color='#667eea')
        self.bar_chart.axes.set_title('Average Parameters')
        self.bar_chart.axes.set_ylabel('Value')
        self.bar_chart.draw()
    
    def load_history(self):
        try:
            headers = {'Authorization': f'Token {self.token}'} if self.token else {}
            response = requests.get(f'{API_BASE_URL}/datasets/', headers=headers)
            
            if response.status_code == 200:
                datasets = response.json()
                self.history_list.clear()
                
                for dataset in datasets:
                    item_text = f"📄 {dataset['filename']} - {dataset['uploaded_at'][:10]} ({dataset['record_count']} records)"
                    self.history_list.addItem(item_text)
                    self.history_list.item(self.history_list.count() - 1).setData(Qt.UserRole, dataset['id'])
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to load history: {str(e)}')
    
    def load_dataset_from_history(self, item):
        dataset_id = item.data(Qt.UserRole)
        self.current_dataset_id = dataset_id
        self.tabs.setCurrentIndex(0)  # Switch to upload tab
        self.load_dataset(dataset_id)
    
    def download_pdf(self):
        if not self.current_dataset_id:
            QMessageBox.warning(self, 'Error', 'No dataset loaded')
            return
        
        try:
            headers = {'Authorization': f'Token {self.token}'} if self.token else {}
            response = requests.get(f'{API_BASE_URL}/datasets/{self.current_dataset_id}/report/', 
                                   headers=headers, stream=True)
            
            if response.status_code == 200:
                filename, _ = QFileDialog.getSaveFileName(self, 'Save PDF', 
                                                         f'equipment_report_{self.current_dataset_id}.pdf',
                                                         'PDF Files (*.pdf)')
                if filename:
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    QMessageBox.information(self, 'Success', 'PDF report downloaded successfully!')
            else:
                QMessageBox.warning(self, 'Error', 'Failed to generate PDF')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Download failed: {str(e)}')


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    main_window = MainWindow()
    login_window = LoginWindow(main_window)
    login_window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()