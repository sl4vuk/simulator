# widgets.py
# Helpers para crear botones y estilos reutilizables

import os
import sys
from PySide6.QtWidgets import QPushButton, QLabel, QFrame
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import QSize

def base_dir():
    if getattr(sys, 'frozen', False):
        # ejecutándose como .exe
        return os.path.dirname(sys.executable)
    else:
        # ejecutándose como script normal
        return os.path.dirname(__file__)

BASE_ASSETS = os.path.join(base_dir(), "assets")

def asset_path(name):
    return os.path.join(BASE_ASSETS, name)

    

def make_button(text, callback=None, icon=None, minimum_height=36):
    btn = QPushButton(text)
    btn.setMinimumHeight(minimum_height)
    btn.setFont(QFont("Segoe UI", 10))
    # estilo minimalista y cuadrado
    btn.setStyleSheet("""
                      
        QPushButton {
            background: #f1f1f1;
            padding: 6px 10px;
            border-radius: 6px;
            color: #000;
        }
        QPushButton:pressed {
            background: #e0e0e0;
            color: #000;
        }

    """)
    if icon:
        try:
            btn.setIcon(QIcon(asset_path(icon)))
            btn.setIconSize(QSize(18, 18))
        except Exception:
            pass
    if callback:
        btn.clicked.connect(callback)
    return btn

def create_top_bar(parent_layout, buttons):
    """
    Crea un frame horizontal con botones.
    buttons = [ (label, icon_name, callback), ... ]
    Retorna el frame creado (QFrame).
    """
    from PySide6.QtWidgets import QHBoxLayout, QFrame
    frame = QFrame()
    layout = QHBoxLayout(frame)
    layout.setContentsMargins(6, 3, 6, 3)
    layout.setSpacing(8)
    for label, icon_name, cb in buttons:
        btn = make_button(label, callback=cb, icon=icon_name, minimum_height=40)
        btn.setObjectName("topButton")
        layout.addWidget(btn)
    layout.addStretch()
    parent_layout.addWidget(frame)
    return frame
