
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import random
import time
from queue import Queue
import threading

class BoundedBuffer:
    def __init__(self, size):
        self.buffer = Queue(maxsize=size)
        self.size = size

        # Y/c loại trừ tương hỗ, semaphore mutex để thoả y/c loại trừ tương hỗ, loại binary.
        self.mutex = threading.Semaphore(1)
        #biến empty nguyên (semaphore nguyên) đếm số lượng ô còn trống trong buffer, khởi tạo = size
        self.empty = threading.Semaphore(size)
        #biến full (semaphore nguyên) đếm số lượng ô có chứa dữ liệu trong buffer, khoi tao =0.
        self.full = threading.Semaphore(0)

    def produce(self, item):
        # entry section
        # hàm wait(empty) until empty>0 và wait (mutex)
        self.empty.acquire()
        self.mutex.acquire()

        #critical section
        # thêm dữ liệu vào buffer
        self.buffer.put(item)

        #exit section
        self.mutex.release()  # lock
        self.full.release()

    def consume(self):
        # entry section
        self.full.acquire()  # wait util full >0 and then dec
        self.mutex.acquire()  # Acquire lock

        #critical section
        # lấy dữ liệu từ buffer
        item = self.buffer.get()

        #exit section
        self.mutex.release()
        self.empty.release()
        return item


class ProducerThread(QThread):
    update_signal = pyqtSignal(str, str, list)

    def __init__(self, buffer, gui):
        super().__init__()
        self.buffer = buffer
        self.gui = gui
        self.running = False

    def run(self):
        while self.running:
            try:
                delay = float(self.gui.producer_speed_input.text())
            except ValueError:
                delay = 3

            item = random.randint(1, 100)
            self.update_signal.emit("Producer: Waiting (Yellow)",
                                    f"Producer waiting to produce {item}\n"
                                    f"Empty slots available: {self.buffer.empty._value}",
                                    list(self.buffer.buffer.queue))
            time.sleep(delay)
            self.update_signal.emit("Producer: Producing (Red)",
                                    f"Producer adding {item} to buffer",
                                    list(self.buffer.buffer.queue))
            self.buffer.produce(item)
            items = list(self.buffer.buffer.queue)
            self.update_signal.emit("Producer: Idle (Green)",
                                    f"Producer successfully produced {item}", items)
            time.sleep(delay)


class ConsumerThread(QThread):
    update_signal = pyqtSignal(str, str, list)

    def __init__(self, buffer, gui):
        super().__init__()
        self.buffer = buffer
        self.gui = gui
        self.running = False

    def run(self):
        while self.running:
            try:
                delay = float(self.gui.consumer_speed_input.text())
            except ValueError:
                delay = 3

            self.update_signal.emit("Consumer: Waiting (Yellow)",
                                    "Consumer waiting to consume",
                                    list(self.buffer.buffer.queue))
            time.sleep(delay)
            self.update_signal.emit("Consumer: Consuming (Red)",
                                    "Consumer removing item from buffer",
                                    list(self.buffer.buffer.queue))
            item = self.buffer.consume()
            items = list(self.buffer.buffer.queue)
            self.update_signal.emit("Consumer: Idle (Green)",
                                    f"Consumer successfully consumed {item}", items)
            time.sleep(delay)