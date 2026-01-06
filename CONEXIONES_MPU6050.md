# 🔌 Conexiones MPU6050 con ESP32 Devkit V1

## 📋 Conexiones Físicas

Conecta el MPU6050 al ESP32 Devkit V1 de la siguiente manera:

```
MPU6050          ESP32 Devkit V1
================================
VCC       --->   3.3V  ⚠️ NO USES 5V!
GND       --->   GND
SCL       --->   GPIO 22
SDA       --->   GPIO 21
XDA       --->   (no conectar)
XCL       --->   (no conectar)
AD0       --->   GND (dirección I2C 0x68)
INT       --->   (no conectar, opcional)
```

### ⚠️ IMPORTANTE:
- **Usa 3.3V, NO 5V** - El ESP32 trabaja a 3.3V
- **AD0 a GND** - Esto establece la dirección I2C en 0x68 (por defecto)
- Los pines SDA/SCL son los pines I2C por defecto del ESP32 Devkit V1

## 📚 Librerías Arduino Necesarias

### 1. Instalar la librería MPU6050

Abre el Arduino IDE y sigue estos pasos:

#### Opción A: Usando el Gestor de Librerías (RECOMENDADO)
1. Ve a **Sketch → Include Library → Manage Libraries**
2. Busca: **"MPU6050"**
3. Instala: **"MPU6050 by Electronic Cats"** o **"MPU6050 by Jeff Rowberg"**
4. También necesitas: **"I2Cdevlib"** (si usas la de Jeff Rowberg)

#### Opción B: Instalación Manual
Si usas la librería de Jeff Rowberg:
1. Descarga el repositorio: https://github.com/jrowberg/i2cdevlib
2. Copia las carpetas `MPU6050` y `I2Cdev` desde `Arduino/` a tu carpeta de librerías Arduino
3. Reinicia el Arduino IDE

### 2. Configuración del ESP32 en Arduino IDE

1. Ve a **File → Preferences**
2. En "Additional Board Manager URLs" agrega:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. Ve a **Tools → Board → Boards Manager**
4. Busca **"esp32"** e instala **"esp32 by Espressif Systems"**
5. Selecciona **Tools → Board → ESP32 Arduino → ESP32 Dev Module**

## 🚀 Pasos para Probar

### 1. Cargar el Firmware

1. Conecta el ESP32 al PC mediante USB
2. Abre `firmware/firmware.ino` en Arduino IDE
3. Configura:
   - **Board:** ESP32 Dev Module
   - **Upload Speed:** 921600
   - **Port:** El puerto COM de tu ESP32
4. Sube el código

### 2. Verificar Comunicación

1. Abre el **Monitor Serial** (115200 baudios)
2. Deberías ver:
   ```
   Inicializando MPU-6050...
   Buscando MPU6050...
   MPU6050 conectado!
   MPU6050 inicializado correctamente
   MPU-6050 listo!
   Calibrando...
   Listo para enviar datos
   ```
3. Luego verás datos en formato:
   ```
   0.012,-0.034,0.998,0.45,1.23,-0.78
   ```

### 3. Ejecutar el Visualizador Python

1. **Identifica tu puerto COM:**
   - Abre el Arduino IDE
   - Ve a **Tools → Port**
   - Anota el puerto (ej: COM3, COM4, etc.)
   - **CIERRA el Monitor Serial del Arduino IDE** antes de ejecutar Python

2. **Edita el archivo Python:**
   - Abre `model/visualize_movement.py`
   - Cambia la línea: `SERIAL_PORT = 'COM3'` por tu puerto

3. **Ejecuta el visualizador:**
   ```bash
   cd model
   python visualize_movement.py
   ```

4. Mueve el MPU6050 y verás el cubo 3D moverse y rotar en tiempo real!

## 🔧 Solución de Problemas

### "MPU6050 no detectado"

1. **Verifica las conexiones:**
   - Asegúrate de que VCC va a 3.3V (NO 5V)
   - Revisa que SDA/SCL estén en los pines correctos
   - Confirma que AD0 está conectado a GND

2. **Prueba el I2C Scanner:**
   ```cpp
   #include <Wire.h>
   
   void setup() {
     Serial.begin(115200);
     Wire.begin(21, 22);
     Serial.println("\nI2C Scanner");
   }
   
   void loop() {
     byte error, address;
     int nDevices = 0;
     
     Serial.println("Escaneando...");
     for(address = 1; address < 127; address++) {
       Wire.beginTransmission(address);
       error = Wire.endTransmission();
       
       if (error == 0) {
         Serial.print("Dispositivo I2C en 0x");
         if (address < 16) Serial.print("0");
         Serial.println(address, HEX);
         nDevices++;
       }
     }
     
     if (nDevices == 0)
       Serial.println("No se encontraron dispositivos I2C");
     else
       Serial.println("Escaneo completo");
       
     delay(5000);
   }
   ```
   - Deberías ver: `Dispositivo I2C en 0x68`

3. **Otros problemas:**
   - Verifica que el MPU6050 no esté dañado
   - Prueba con cables más cortos
   - Asegúrate de que el ESP32 esté alimentado correctamente

### "Puerto COM ocupado" en Python

- **Cierra el Monitor Serial** del Arduino IDE antes de ejecutar Python
- Si sigue ocupado, desconecta y reconecta el ESP32

### El cubo no se mueve correctamente

- Verifica que el baudrate sea 115200 en ambos lados
- Asegúrate de que el MPU6050 esté bien calibrado (déjalo quieto al inicio)
- Revisa que los datos lleguen correctamente al Python

## 📊 Formato de Datos

El ESP32 envía datos por Serial en formato CSV:
```
ax,ay,az,yaw,pitch,roll
```

Donde:
- **ax, ay, az**: Aceleración en g's (-2 a +2)
- **yaw**: Rotación en eje Z (grados)
- **pitch**: Rotación en eje Y (grados)
- **roll**: Rotación en eje X (grados)

## 🎯 Frecuencia de Muestreo

- **Actual:** 20 Hz (50ms de delay)
- Puedes ajustarlo en `firmware.ino` cambiando el `delay(50)`
- A menor delay, mayor frecuencia pero más carga en el serial

## ✅ Checklist Final

- [ ] MPU6050 conectado correctamente a 3.3V
- [ ] AD0 conectado a GND
- [ ] SDA → GPIO 21, SCL → GPIO 22
- [ ] Librería MPU6050 instalada en Arduino IDE
- [ ] ESP32 board package instalado
- [ ] Firmware cargado y funcionando
- [ ] Monitor Serial muestra datos (115200 baudios)
- [ ] Monitor Serial CERRADO antes de ejecutar Python
- [ ] Puerto COM correcto en visualize_movement.py
- [ ] Python ejecutándose y mostrando visualización

¡Ahora deberías poder ver tu MPU6050 visualizado en 3D! 🎉
