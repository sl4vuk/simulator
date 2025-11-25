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

### Fuerza de arrastre del aire

```math
F*d = 0.5 * ρ _ C_d _ A \_ v^2
```

### Aceleraciones

En el eje X:

```math
a_x = (-F_d / m) \* (v_x / v)
```

En el eje Y:

```math
a_y = -g + (-F_d / m) \* (v_y / v)
```

### Integración numérica

La velocidad y posición se actualizan usando integración de Euler con paso dt:

```math
v = v + a \* dt
```

```math
x = x + v \* dt
```
