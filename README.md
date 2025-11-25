# 🔰 Simulador de Movimiento Parabólico

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

- Fuerza de arrastre del aire

$$
\vec{F}_d = -\tfrac{1}{2} \rho C_d A v^2 \, \hat{v}
$$

- Ecuaciones en el eje X

$$
a_x = -\,\frac{F_d}{m}\,\frac{v_x}{v}
$$

- Ecuaciones en el eje Y

$$
a_y = -g - \frac{F_d}{m}\,\frac{v_y}{v}
$$

- Integración numérica (Método de Euler)

Actualización de la velocidad:

$$
\vec{v} = \vec{v} + \vec{a}\,\Delta t
$$

Actualización de la posición:

$$
\vec{x} = \vec{x} + \vec{v}\,\Delta t
$$

---
