[![Chat-GPT-Image-Nov-25-2025-05-29-48-AM.png](https://i.postimg.cc/qv05BGv0/Chat-GPT-Image-Nov-25-2025-05-29-48-AM.png)](https://postimg.cc/ppGZqzj1)

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

### Launch Command

```ps1
python gui.py
```

### Requirements

```ps1
pip install PySide6 matplotlib numpy
```

> [!NOTE]
> Usar python 3.12 en adelante

---

## 📚 Física aplicada

- Fuerza de arrastre del aire

$$
\vec{F}_d = -\tfrac{1}{2} \rho C_d A v^2 \, \hat{v}
$$

1. **Posición:**

   - Ecuaciones en el eje X

   $$
   a_x = -\,\frac{F_d}{m}\,\frac{v_x}{v}
   $$

   - Ecuaciones en el eje Y

   $$
   a_y = -g - \frac{F_d}{m}\,\frac{v_y}{v}
   $$

2. **Integración numérica (Método de Euler)**

   Actualización de la velocidad:

   $$
   \vec{v} = \vec{v} + \vec{a}\,\Delta t
   $$

   Actualización de la posición:

   $$
   \vec{x} = \vec{x} + \vec{v}\,\Delta t
   $$
