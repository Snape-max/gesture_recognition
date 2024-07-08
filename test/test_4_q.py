from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider
from PyQt5.QtCore import Qt

app = QApplication([])
window = QWidget()

slider = QSlider(Qt.Horizontal)

layout = QVBoxLayout(window)
layout.addWidget(slider)

window.show()
app.exec_()
