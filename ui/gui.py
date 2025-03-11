import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QTextEdit, QLineEdit)
from PyQt5.QtCore import Qt
from BoundedBuffer import BoundedBuffer, ProducerThread, ConsumerThread


class BufferGUI(QMainWindow):
    def __init__(self, buffer_size=5):
        super().__init__()
        self.buffer = BoundedBuffer(buffer_size)
        self.buffer_size = buffer_size
        self.log_counter = 1
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Bounded Buffer Problem Visualization")
        self.setGeometry(100, 100, 1000, 500)
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Buffer slots
        buffer_frame = QWidget()
        buffer_layout = QHBoxLayout(buffer_frame)
        self.buffer_slots = []
        for _ in range(self.buffer_size):
            slot = QLabel("Empty")
            slot.setAlignment(Qt.AlignCenter)
            slot.setStyleSheet("""
                border: 2px solid black;
                background-color: white;
                min-width: 100px;
                min-height: 50px;
                font-size: 16px;
                font-weight: bold;
            """)
            buffer_layout.addWidget(slot)
            self.buffer_slots.append(slot)
        layout.addWidget(buffer_frame)

        # Status labels
        status_frame = QWidget()
        status_layout = QHBoxLayout(status_frame)
        self.producer_status = QLabel("Producer: Idle (Green)")
        self.consumer_status = QLabel("Consumer: Idle (Green)")
        status_layout.addWidget(self.producer_status)
        status_layout.addWidget(self.consumer_status)
        layout.addWidget(status_frame)

        # Speed input fields
        speed_frame = QWidget()
        speed_layout = QHBoxLayout(speed_frame)
        self.producer_speed_label = QLabel("Producer Speed (sec):")
        self.producer_speed_input = QLineEdit("3")
        self.consumer_speed_label = QLabel("Consumer Speed (sec):")
        self.consumer_speed_input = QLineEdit("3")
        speed_layout.addWidget(self.producer_speed_label)
        speed_layout.addWidget(self.producer_speed_input)
        speed_layout.addWidget(self.consumer_speed_label)
        speed_layout.addWidget(self.consumer_speed_input)
        layout.addWidget(speed_frame)

        # Logs
        log_frame = QWidget()
        log_layout = QHBoxLayout(log_frame)
        self.producer_log = QTextEdit()
        self.producer_log.setReadOnly(True)
        self.consumer_log = QTextEdit()
        self.consumer_log.setReadOnly(True)
        log_layout.addWidget(QLabel("Producer Log:"))
        log_layout.addWidget(self.producer_log)
        log_layout.addWidget(QLabel("Consumer Log:"))
        log_layout.addWidget(self.consumer_log)
        layout.addWidget(log_frame)

        # Start & Stop buttons
        button_frame = QWidget()
        button_layout = QHBoxLayout(button_frame)
        self.start_btn = QPushButton("Start Simulation")
        self.start_btn.clicked.connect(self.start_simulation)
        button_layout.addWidget(self.start_btn)
        self.stop_btn = QPushButton("Stop Simulation")
        self.stop_btn.clicked.connect(self.stop_simulation)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        layout.addWidget(button_frame)

        # Threads
        self.producer_thread = ProducerThread(self.buffer, self)
        self.consumer_thread = ConsumerThread(self.buffer, self)
        self.producer_thread.update_signal.connect(self.update_ui)
        self.consumer_thread.update_signal.connect(self.update_ui)

    def update_ui(self, status, log_text, items):
        sender = self.sender()
        log_entry = f"[{self.log_counter}] {log_text}"
        self.log_counter += 1
        if sender == self.producer_thread:
            self.producer_status.setText(status)
            self.producer_log.append(log_entry)
        else:
            self.consumer_status.setText(status)
            self.consumer_log.append(log_entry)
        self.update_buffer_ui(items)

    def update_buffer_ui(self, items):
        reversed_items = list(reversed(items))
        for i in range(self.buffer_size):
            if i < len(reversed_items):
                self.buffer_slots[i].setText(str(reversed_items[i]))
                self.buffer_slots[i].setStyleSheet("background-color: lightgreen; border: 1px solid black;")
            else:
                self.buffer_slots[i].setText("Empty")
                self.buffer_slots[i].setStyleSheet("background-color: white; border: 1px solid black;")

    def start_simulation(self):
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.producer_thread.running = True
        self.consumer_thread.running = True
        self.producer_thread.start()
        self.consumer_thread.start()

    def stop_simulation(self):
        self.producer_thread.running = False
        self.consumer_thread.running = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BufferGUI()
    window.show()
    sys.exit(app.exec_())
