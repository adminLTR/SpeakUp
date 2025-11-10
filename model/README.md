# Visualizador de Movimiento MPU-6050

Este módulo contiene herramientas para visualizar en tiempo real los datos del sensor MPU-6050.

## Instalación

1. Instala las dependencias de Python:
```bash
pip install -r requirements.txt
```

## Uso del Visualizador 3D

### 1. Carga el firmware en Arduino
Primero, carga el código del firmware en tu Arduino con el MPU-6050 conectado.

### 2. Identifica tu puerto serial
- **Windows**: Abre el IDE de Arduino y ve a `Herramientas > Puerto`. Verás algo como `COM3`, `COM4`, etc.
- **Linux/Mac**: Generalmente es `/dev/ttyUSB0` o `/dev/ttyACM0`

### 3. Configura el puerto en el script
Edita `visualize_movement.py` y cambia la línea:
```python
SERIAL_PORT = 'COM3'  # Cambia por tu puerto
```

### 4. Ejecuta el visualizador
```bash
python visualize_movement.py
```

## Qué verás

El visualizador muestra dos paneles:

### Panel Izquierdo (3D)
- **Cubo azul**: Representa tu objeto/guante con su orientación actual
- **Línea cyan**: Trayectoria del movimiento en el plano XZ
- El cubo rota según los ángulos Yaw, Pitch y Roll

### Panel Derecho (Gráfica 2D)
- **Línea roja**: Yaw (rotación en Z)
- **Línea verde**: Pitch (rotación en Y)
- **Línea azul**: Roll (rotación en X)

## Formato de datos

El firmware envía datos por serial en formato CSV:
```
x,z,yaw,pitch,roll
```

Donde:
- `x`, `z`: Aceleración en ejes X y Z (en g's)
- `yaw`, `pitch`, `roll`: Ángulos de rotación (en grados)

## Solución de problemas

### Error de puerto serial
Si obtienes un error de conexión serial, verifica:
1. Que el Arduino esté conectado
2. Que el puerto sea el correcto
3. Que no tengas el Monitor Serial del Arduino IDE abierto (solo un programa puede usar el puerto a la vez)

### Los datos no se muestran correctamente
1. Cierra el script de Python
2. Abre el Monitor Serial del Arduino IDE y verifica que los datos se envíen correctamente
3. Cierra el Monitor Serial y vuelve a ejecutar el script de Python