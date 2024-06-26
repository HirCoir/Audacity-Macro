import sys
import os
import pyautogui
import keyboard
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QObject, pyqtSlot, pyqtSignal
from PyQt5.QtWebChannel import QWebChannel

class WebChannelBridge(QObject):
    toggleStateChanged = pyqtSignal(bool)

    @pyqtSlot()
    def toggleScript(self):
        ex.toggle_script()

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.script_active = False
        self.hotkey = 'w'

    def initUI(self):
        self.setWindowTitle('Audacity Macro')
        self.setGeometry(100, 100, 400, 300)
        self.setFixedSize(400, 300)  # Bloquear el tamaño de la ventana

        # Configurar el icono de la ventana
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        self.layout = QVBoxLayout()

        self.label = QLabel('Macro inactivo', self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: white;")
        self.layout.addWidget(self.label)

        self.web_view = QWebEngineView()
        self.channel = QWebChannel()
        self.bridge = WebChannelBridge()
        self.channel.registerObject('bridge', self.bridge)
        self.web_view.page().setWebChannel(self.channel)
        self.web_view.setHtml('''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {
                        background-color: black;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                    }
                    .toggler {
                      width: 72px;
                      margin: 40px auto;
                    }

                    .toggler input {
                      display: none;
                    }

                    .toggler label {
                      display: block;
                      position: relative;
                      width: 72px;
                      height: 36px;
                      border: 1px solid #d6d6d6;
                      border-radius: 36px;
                      background: #e4e8e8;
                      cursor: pointer;
                    }

                    .toggler label::after {
                      display: block;
                      border-radius: 100%;
                      background-color: #d7062a;
                      content: '';
                      animation-name: toggler-size;
                      animation-duration: 0.15s;
                      animation-timing-function: ease-out;
                      animation-direction: forwards;
                      animation-iteration-count: 1;
                      animation-play-state: running;
                    }

                    .toggler label::after, .toggler label .toggler-on, .toggler label .toggler-off {
                      position: absolute;
                      top: 50%;
                      left: 25%;
                      width: 26px;
                      height: 26px;
                      transform: translateY(-50%) translateX(-50%);
                      transition: left 0.15s ease-in-out, background-color 0.2s ease-out, width 0.15s ease-in-out, height 0.15s ease-in-out, opacity 0.15s ease-in-out;
                    }

                    .toggler input:checked + label::after, .toggler input:checked + label .toggler-on, .toggler input:checked + label .toggler-off {
                      left: 75%;
                    }

                    .toggler input:checked + label::after {
                      background-color: #50ac5d;
                      animation-name: toggler-size2;
                    }

                    .toggler .toggler-on, .toggler .toggler-off {
                      opacity: 1;
                      z-index: 2;
                    }

                    .toggler input:checked + label .toggler-off, .toggler input:not(:checked) + label .toggler-on {
                      width: 0;
                      height: 0;
                      opacity: 0;
                    }

                    .toggler .path {
                      fill: none;
                      stroke: #fefefe;
                      stroke-width: 7px;
                      stroke-linecap: round;
                      stroke-miterlimit: 10;
                    }

                    @keyframes toggler-size {
                      0%, 100% {
                        width: 26px;
                        height: 26px;
                      }

                      50% {
                        width: 20px;
                        height: 20px;
                      }
                    }

                    @keyframes toggler-size2 {
                      0%, 100% {
                        width: 26px;
                        height: 26px;
                      }

                      50% {
                        width: 20px;
                        height: 20px;
                      }
                    }
                </style>
                <script src="https://cdn.jsdelivr.net/npm/qwebchannel/qwebchannel.js"></script>
            </head>
            <body>
                <div class="toggler">
                    <input id="toggler-1" name="toggler-1" type="checkbox" value="1">
                    <label for="toggler-1" onclick="pyqt_toggle_script()">
                        <svg class="toggler-on" version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 130.2 130.2">
                            <polyline class="path check" points="100.2,40.2 51.5,88.8 29.8,67.5"></polyline>
                        </svg>
                        <svg class="toggler-off" version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 130.2 130.2">
                            <line class="path line" x1="34.4" y1="34.4" x2="95.8" y2="95.8"></line>
                            <line class="path line" x1="95.8" y1="34.4" x2="34.4" y2="95.8"></line>
                        </svg>
                    </label>
                </div>
                <script>
                    function pyqt_toggle_script() {
                        new QWebChannel(qt.webChannelTransport, function (channel) {
                            var bridge = channel.objects.bridge;
                            bridge.toggleScript();
                        });
                    }
                    
                    function setTogglerState(isChecked) {
                        document.getElementById('toggler-1').checked = isChecked;
                    }
                </script>
            </body>
            </html>
        ''')

        self.layout.addWidget(self.web_view)

        self.hotkey_layout = QHBoxLayout()
        self.hotkey_label = QLabel('Establecer tecla:', self)
        self.hotkey_label.setStyleSheet("color: white;")
        self.hotkey_input = QLineEdit(self)
        self.hotkey_input.setPlaceholderText('Ingrese una clave (por ejemplo, w)')
        self.hotkey_input.setMaxLength(1)
        self.hotkey_input.setStyleSheet("color: white; background-color: black; border: 1px solid white;")
        self.hotkey_input.textChanged.connect(self.update_hotkey)

        self.hotkey_layout.addWidget(self.hotkey_label)
        self.hotkey_layout.addWidget(self.hotkey_input)
        self.layout.addLayout(self.hotkey_layout)

        self.setLayout(self.layout)
        self.setStyleSheet("background-color: black;")

    def toggle_script(self):
        if not self.script_active:
            if self.hotkey_input.text() == '':
                self.show_warning_message('Error', 'Ingrese una tecla de acceso rápido antes de activar el script.')
                self.web_view.page().runJavaScript('setTogglerState(false);')
                return
            self.label.setText('Macro activo')
            self.script_active = True
            self.start_listening()
        else:
            self.label.setText('Macro inactivo')
            self.script_active = False
            self.stop_listening()

    def show_warning_message(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStyleSheet("QLabel { color: white; }"
                              "QMessageBox { background-color: black; }"
                              "QPushButton { background-color: #444; color: white; border: none; padding: 5px 10px; }"
                              "QPushButton:hover { background-color: #666; }")
        msg_box.exec_()

    def update_hotkey(self, text):
        self.hotkey = text

    def start_listening(self):
        if self.script_active:
            keyboard.on_press_key(self.hotkey, self.on_press_key)

    def stop_listening(self):
        keyboard.unhook_all()

    def on_press_key(self, event):
        if self.script_active and event.name == self.hotkey:
            keyboard.block_key(self.hotkey)
            pyautogui.hotkey('ctrl', 'b')
            pyautogui.press('esc')
            keyboard.unblock_key(self.hotkey)

def main():
    global ex
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
