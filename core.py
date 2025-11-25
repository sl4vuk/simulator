# core.py
# Motor físico: simulador 2D con arrastre cuadrático y viento
# Exporta la clase ProjectileSimulator

import math
import numpy as np

class ProjectileSimulator:
    """
    Simula un proyectil en 2D con arrastre cuadrático y viento horizontal constante.
    Uso:
        sim = ProjectileSimulator(v0=30, angle_deg=45, mass=1.0, area=0.01, cd=0.47, wind=0.0, g=9.81, dt=0.01)
        while not sim.finished:
            sim.step()
            estado = sim.get_state()  # diccionario con datos
    """
    def __init__(self, v0=30.0, angle_deg=45.0, mass=1.0, area=0.01, cd=0.47,
                 wind=0.0, g=9.81, rho=1.225, dt=0.01, max_time=300.0, y0=0.0):
        # parámetros físicos
        self.mass = float(mass)
        self.area = float(area)
        self.cd = float(cd)
        self.wind = float(wind)         # viento (m/s), positivo hacia +x
        self.g = float(g)
        self.rho = float(rho)
        self.dt = float(dt)
        self.max_time = float(max_time)

        # estado inicial
        self.v0 = float(v0)
        self.angle = math.radians(float(angle_deg))
        self.x = 0.0
        self.y = float(y0)
        self.vx = self.v0 * math.cos(self.angle)
        self.vy = self.v0 * math.sin(self.angle)
        self.t = 0.0

        self.finished = False

    def _drag_force(self, vx, vy):
        """
        Calcula la fuerza de arrastre (Fx, Fy) aplicada por el fluido
        usando modelo cuadrático: Fd = 0.5 * rho * Cd * A * v_rel^2
        dirección opuesta a la velocidad relativa al aire (incluye viento).
        """
        vrel_x = vx - self.wind
        vrel_y = vy
        vrel = math.hypot(vrel_x, vrel_y)
        if vrel == 0:
            return 0.0, 0.0
        Fd = 0.5 * self.rho * self.cd * self.area * vrel * vrel
        fx = -Fd * (vrel_x / vrel)
        fy = -Fd * (vrel_y / vrel)
        return fx, fy

    def step(self):
        """Avanza la simulación un paso dt usando Euler explícito (suficiente y rápido)."""
        if self.finished:
            return

        # fuerzas
        fx_drag, fy_drag = self._drag_force(self.vx, self.vy)
        fx_total = fx_drag
        fy_total = fy_drag - self.mass * self.g

        # aceleraciones
        ax = fx_total / self.mass
        ay = fy_total / self.mass

        # actualizar velocidades y posiciones
        self.vx += ax * self.dt
        self.vy += ay * self.dt
        self.x += self.vx * self.dt
        self.y += self.vy * self.dt
        self.t += self.dt

        # condiciones de parada: suelo (y <= 0) o tiempo maximo
        if self.y <= 0.0 and self.t > 0.0:
            # interpolación para ajustar a y=0 más precisamente
            # retrocedemos un paso y hacemos interpolación lineal entre prev y actual
            # (nota: guardamos estado anterior aproximado)
            self.y = 0.0
            self.finished = True

        if self.t >= self.max_time:
            self.finished = True

    def acceleration(self):
        fx_drag, fy_drag = self._drag_force(self.vx, self.vy)
        ax = fx_drag / self.mass
        ay = (fy_drag - self.mass * self.g) / self.mass
        return ax, ay

    def force(self):
        fx_drag, fy_drag = self._drag_force(self.vx, self.vy)
        # añadir peso como componente en Fy total
        fy_total = fy_drag - self.mass * self.g
        return fx_drag, fy_total

    def speed(self):
        return math.hypot(self.vx, self.vy)

    def kinetic_energy(self):
        v = self.speed()
        return 0.5 * self.mass * v * v

    def potential_energy(self):
        # referencia y=0 -> energia potencial = mgy
        return self.mass * self.g * max(0.0, self.y)

    def total_energy(self):
        return self.kinetic_energy() + self.potential_energy()

    def get_state(self):
        """Devuelve un dic con el estado actual (listo para UI)."""
        ax, ay = self.acceleration()
        fx, fy = self.force()
        return {
            "time": self.t,
            "pos": (self.x, self.y),
            "vel": (self.vx, self.vy),
            "speed": self.speed(),
            "acc": (ax, ay),
            "force": (fx, fy),
            "energy": {
                "kin": self.kinetic_energy(),
                "pot": self.potential_energy(),
                "total": self.total_energy()
            },
            "finished": self.finished
        }
