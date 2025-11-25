# 🔰 Simulador de Movimiento Parabólico (PySide6)

Simulador educativo del movimiento parabólico con resistencia del aire, viento y parámetros físicos ajustables, con visualización en tiempo real mediante Matplotlib y una interfaz minimalista en PySide6.

---

## 📝 Descripción

El programa calcula la trayectoria de un proyectil lanzado con velocidad inicial y ángulo dado, considerando:

- Gravedad
- Arrastre cuadrático del aire
- Viento horizontal
- Integración numérica paso a paso

Incluye animación de la trayectoria y lectura visual de datos como alcance, altura máxima, velocidad y energía.

---

## 📚 Física aplicada

Fuerza de arrastre del aire:

F*d = 0.5 * ρ _ Cd _ A \_ v²

Aceleraciones:

ax = (-F*d / m) * (vx / v)
ay = -g + (-F*d / m) * (vy / v)

Velocidad y posición se actualizan usando integración de Euler con paso `dt`.
