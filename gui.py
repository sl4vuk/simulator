# gui.py
# Interfaz PySide6 que usa core.py y widgets.py
# Ejecutar: python gui.py

import os
import sys
from math import hypot
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout,
    QGridLayout, QFrame, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QFont, QIcon, QPalette, QColor

from core import ProjectileSimulator
from widgets import make_button, asset_path, create_top_bar

# Matplotlib canvas
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class SimuladorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("APP")
        self.setFixedSize(1000, 640)
        self._apply_styles()

        self.sim = None
        self.timer = QTimer()
        self.timer.timeout.connect(self._step_sim)

        # layout principal (vertical to include topbar)
        root = QVBoxLayout(self)
        root.setContentsMargins(6,6,6,6)
        root.setSpacing(6)

        # top bar (using widgets.create_top_bar)
        # we'll attach callbacks after building GUI elements
        top_buttons = []  # placeholder -> we'll fill with references later
        top_frame = QFrame()
        top_layout = QHBoxLayout(top_frame)
        top_layout.setContentsMargins(6,3,6,3)
        top_layout.setSpacing(8)
        root.addWidget(top_frame)

        # main split: left inputs + results; right plot
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)
        root.addLayout(main_layout, stretch=1)

        # LEFT panel: inputs and dynamic readers
        left_frame = QFrame()
        left_frame.setObjectName("panelLeft")
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(10,10,10,10)
        left_layout.setSpacing(8)

        title = QLabel("Parámetros")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        left_layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(6)
        left_layout.addLayout(grid)

        def add_row(r, label, default=""):
            lbl = QLabel(label)
            lbl.setFont(QFont("Segoe UI", 10))
            edit = QLineEdit()
            edit.setText(str(default))
            edit.setFixedHeight(28)
            grid.addWidget(lbl, r, 0)
            grid.addWidget(edit, r, 1)
            return edit

        self.in_v0 = add_row(0, "Velocidad inicial (m/s):", "30")
        self.in_angle = add_row(1, "Ángulo (°):", "45")
        self.in_mass = add_row(2, "Masa (kg):", "1.0")
        self.in_area = add_row(3, "Área frontal (m²):", "0.01")
        self.in_cd = add_row(4, "Coef. arrastre (Cd):", "0.47")
        self.in_wind = add_row(5, "Viento (m/s):", "0.0")
        self.in_g = add_row(6, "Gravedad (m/s²):", "9.81")
        self.in_rho = add_row(7, "Densidad aire ρ (kg/m³):", "1.225")
        self.in_dt = add_row(8, "Paso dt (s):", "0.01")

        # action buttons (left)
        actions_layout = QHBoxLayout()
        self.btn_simulate = make_button("Simular", callback=self._on_simulate, icon="simulate.png")
        self.btn_play = make_button("Play", callback=self._on_play_pause, icon="play.png")
        self.btn_play.setEnabled(False)
        actions_layout.addWidget(self.btn_simulate)
        actions_layout.addWidget(self.btn_play)
        left_layout.addLayout(actions_layout)

        # results (static summary)
        left_layout.addSpacing(6)
        res_title = QLabel("Resultados")
        res_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        left_layout.addWidget(res_title)

        self.lbl_time = QLabel("Tiempo: — s")
        self.lbl_pos = QLabel("Pos (x,y): — , —")
        self.lbl_speed = QLabel("Velocidad |v|: — m/s")
        self.lbl_acc = QLabel("Aceleración (ax,ay): — , —")
        self.lbl_force = QLabel("Fuerza (Fx,Fy): — , —")
        self.lbl_energy = QLabel("Energía (K, P, T): — , — , —")

        for lbl in (self.lbl_time, self.lbl_pos, self.lbl_speed, self.lbl_acc, self.lbl_force, self.lbl_energy):
            lbl.setFont(QFont("Segoe UI", 10))
            left_layout.addWidget(lbl)

        # dynamic details area (replaced by top bar buttons)
        left_layout.addSpacing(6)
        self.dynamic_label = QLabel("")
        self.dynamic_label.setWordWrap(True)
        self.dynamic_label.setFont(QFont("Segoe UI", 10))
        left_layout.addWidget(self.dynamic_label)

        left_layout.addStretch()
        main_layout.addWidget(left_frame, stretch=1)

        # RIGHT panel: plot
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(6,6,6,6)

        self.fig = Figure(figsize=(6,4), tight_layout=True)
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("x (m)")
        self.ax.set_ylabel("y (m)")
        self.ax.grid(True, linestyle="--", alpha=0.5)
        right_layout.addWidget(self.canvas)

        main_layout.addWidget(right_frame, stretch=2)

        # build top bar buttons now that UI exists
        # callbacks reference self methods that update dynamic_label and control play/pause
        top_items = [
            ("Coordenadas", "coordinates.png", self._show_coordinates),
            ("Velocidad", "speed.png", self._show_speed),
            ("Aceleración", "acceleration.png", self._show_acc),
            ("Fuerza", "strong.png", self._show_force),
            ("Energía", "energy.png", self._show_energy),
        ]
        # add buttons to top_layout
        for label, icon_name, cb in top_items:
            btn = make_button(label, callback=cb, icon=icon_name)
            btn.setMinimumWidth(110)
            top_layout.addWidget(btn)
            # keep reference to play top button to toggle icon/text
            if label.lower() == "play":
                self.top_play_btn = btn
        top_layout.addStretch()

        # internal data holder for plotting
        self._plot_x = []
        self._plot_y = []
        self._plot_line = None
        self._plot_point = None

    def _apply_styles(self):
        # estilo general: claro y minimalista, botones cuadrados
        css = """
        QFrame#topBar {
            background: #d8d8d8;   /* Gris claro pero no tan claro */
        }

        QPushButton#topButton {
            background: #ececec;
            border-radius: 6px;
            padding: 3px 8px;
            color: #000;
        }

        QPushButton#topButton:hover {
            background: #e2e2e2;
            color: #000;
        }

        QWidget {
            background: #000;
            color: #fff;
            font-family: Arial;
            font-size: 12px;
        }
        QFrame#panelLeft {
            background: #000;
        }
        QFrame#panelRight {
            background: #ffffff;
        }
        QLineEdit#inputField {
            background: #1c1c1c;
            padding: 4px;
            border-radius: 6px; /* cuadrado */
        }
        QLineEdit {
            background: #1c1c1c;
            padding: 4px;
            border-radius: 6px; /* cuadrado */
        }
        QLabel {
            color: #fff;
        }
        """
        self.setStyleSheet(css)

    # -----------------------------
    # Top-button dynamic content (example values or real if sim exists)
    # -----------------------------
    def _show_coordinates(self):
        if self.sim:
            st = self.sim.get_state()
            x, y = st["pos"]
            txt = f"<span style='color:#ef4136'><b>💢 Coordenadas:</b><br>x = {x:.2f} m (horizontal)<br>y = {y:.2f} m (vertical)</span>"
        else:
            txt = "<b>Coordenadas:</b><br>x = — m<br>y = — m"
        self.dynamic_label.setText(txt)

    def _show_speed(self):
        if self.sim:
            st = self.sim.get_state()
            vx, vy = st["vel"]
            mag = st["speed"]
            txt = (f"<span style='color:#38b6ff'><b>💠 Velocidad:</b><br>"
                   f"vx = {vx:.2f} m/s<br>vy = {vy:.2f} m/s<br><br>"
                   f"<b>Magnitud:</b> {mag:.2f} m/s")
        else:
            txt = "<b>Velocidad:</b><br>—"
        self.dynamic_label.setText(txt)

    def _show_acc(self):
        if self.sim:
            st = self.sim.get_state()
            ax, ay = st["acc"]
            txt = f"<span style='color:#9d74ee'><b>♐ Aceleración:</b><br>{ax:.2f} m/s², {ay:.2f} m/s²"
        else:
            txt = "<b>Aceleración:</b><br>—"
        self.dynamic_label.setText(txt)

    def _show_force(self):
        if self.sim:
            st = self.sim.get_state()
            fx, fy = st["force"]
            txt = f"<span style='color:#ffb02c'><b>🔶 Fuerza:</b><br>{fx:.2f} N, {fy:.2f} N"
        else:
            txt = "<b>Fuerza:</b><br>—"
        self.dynamic_label.setText(txt)

    def _show_energy(self):
        if self.sim:
            st = self.sim.get_state()
            kin = st["energy"]["kin"]
            pot = st["energy"]["pot"]
            tot = st["energy"]["total"]
            txt = (f"<span style='color:#7fcc28'><b>♻ Energía cinética:</b> {kin:.2f} J<br>"
                   f"<b>Energía potencial:</b> {pot:.2f} J<br>"
                   f"<b>Energía total:</b> {tot:.2f} J")
        else:
            txt = "<b>Energía:</b><br>—"
        self.dynamic_label.setText(txt)

    # -----------------------------
    # Actions: simulate, play/pause
    # -----------------------------
    def _on_simulate(self):
        # call same logic as left simulate
        self._start_simulation(show_message=False)

    def _start_simulation(self, show_message=True):
        try:
            v0 = float(self.in_v0.text())
            angle = float(self.in_angle.text())
            mass = float(self.in_mass.text())
            area = float(self.in_area.text())
            cd = float(self.in_cd.text())
            wind = float(self.in_wind.text())
            g = float(self.in_g.text())
            rho = float(self.in_rho.text())
            dt = float(self.in_dt.text())
        except Exception as e:
            if show_message:
                QMessageBox.critical(self, "Error", f"Parámetros inválidos: {e}")
            return

        # create simulator
        self.sim = ProjectileSimulator(v0=v0, angle_deg=angle, mass=mass, area=area,
                                       cd=cd, wind=wind, g=g, rho=rho, dt=dt)
        # reset plotting buffers
        self._plot_x = []
        self._plot_y = []
        self.ax.clear()
        self.ax.set_xlabel("x (m)")
        self.ax.set_ylabel("y (m)")
        self.ax.grid(True, linestyle="--", alpha=0.5)
        self._plot_line, = self.ax.plot([], [], linewidth=2.0)
        self._plot_point, = self.ax.plot([], [], marker='o', markersize=6)
        self.canvas.draw_idle()

        # enable play button
        self.btn_play.setEnabled(True)
        if hasattr(self, "top_play_btn"):
            self.top_play_btn.setEnabled(True)
            self.top_play_btn.setText("Play")

        # update status
        self.lbl_time.setText("Tiempo: 0.00 s")
        self.lbl_pos.setText("Pos (x,y): 0.00, 0.00")
        self.lbl_speed.setText("Velocidad |v|: — m/s")
        self.lbl_acc.setText("Aceleración (ax,ay): — , —")
        self.lbl_force.setText("Fuerza (Fx,Fy): — , —")
        self.lbl_energy.setText("Energía (K, P, T): — , — , —")

        # auto-start timer (optional). We'll not start automatically; wait for Play.
        # self.timer.start(int(self.sim.dt * 1000))
        if show_message:
            QMessageBox.information(self, "Simulación", "Simulación lista. Pulse Play para ejecutar.")

    def _on_play_pause(self):
        if not self.sim:
            QMessageBox.warning(self, "Aviso", "No hay simulación cargada. Pulse Simular primero.")
            return

        if self.timer.isActive():
            self.timer.stop()
            self.btn_play.setText("Play")
            if hasattr(self, "top_play_btn"):
                self.top_play_btn.setText("Play")
        else:
            # start timer with sim.dt interval (in ms)
            self.timer.start(max(10, int(self.sim.dt * 1000)))
            self.btn_play.setText("Pause")
            if hasattr(self, "top_play_btn"):
                self.top_play_btn.setText("Pause")

    def _step_sim(self):
        if not self.sim or self.sim.finished:
            self.timer.stop()
            self.btn_play.setText("Play")
            if hasattr(self, "top_play_btn"):
                self.top_play_btn.setText("Play")
            return

        # advance simulation
        self.sim.step()
        st = self.sim.get_state()

        # update readers
        self.lbl_time.setText(f"Tiempo: {st['time']:.2f} s")
        x, y = st['pos']
        self.lbl_pos.setText(f"Pos (x,y): {x:.2f}, {y:.2f}")
        self.lbl_speed.setText(f"Velocidad |v|: {st['speed']:.2f} m/s")
        ax, ay = st['acc']
        self.lbl_acc.setText(f"Aceleración (ax,ay): {ax:.2f}, {ay:.2f}")
        fx, fy = st['force']
        self.lbl_force.setText(f"Fuerza (Fx,Fy): {fx:.2f}, {fy:.2f}")
        kin = st['energy']['kin']
        pot = st['energy']['pot']
        tot = st['energy']['total']
        self.lbl_energy.setText(f"Energía (K, P, T): {kin:.2f}, {pot:.2f}, {tot:.2f}")

        # update dynamic label if user requested previously
        # (we leave it unchanged here; top buttons update it on demand)

        # update plotting buffers
        self._plot_x.append(x)
        self._plot_y.append(y)
        self._plot_line.set_data(self._plot_x, self._plot_y)
        self._plot_point.set_data([x], [y])

        # auto-scale y min 0
        ymin = 0.0
        ymax = max(1.0, max(self._plot_y) * 1.05)
        xmax = max(1.0, max(self._plot_x) * 1.05)
        self.ax.set_xlim(0, xmax)
        self.ax.set_ylim(ymin, ymax)

        self.canvas.draw_idle()

        # stop when finished
        if st["finished"]:
            self.timer.stop()
            self.btn_play.setText("Play")
            if hasattr(self, "top_play_btn"):
                self.top_play_btn.setText("Play")
            QMessageBox.information(self, "Finalizado", "El proyectil ha tocado el suelo.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pal = QPalette()
    pal.setColor(QPalette.Window, QColor(17,17,17))
    pal.setColor(QPalette.WindowText, QColor(255,255,255))
    pal.setColor(QPalette.Base, QColor(26,26,26))
    pal.setColor(QPalette.Button, QColor(40,40,40))
    pal.setColor(QPalette.ButtonText, QColor(255,255,255))
    pal.setColor(QPalette.Highlight, QColor(0,120,215))
    app.setPalette(pal)
    win = SimuladorWindow()
    win.show()
    sys.exit(app.exec())
