"""
Visualizador 2D optimizado - Más rápido que 3D
Solo gráficos 2D de ángulos en tiempo real
"""

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import serial
import serial.tools.list_ports
import sys
import time
from collections import deque

SERIAL_PORT = 'COM8'  # Se autodetectará si no está disponible
BAUD_RATE = 115200
MAX_POINTS = 100  # Histórico de puntos

def find_available_port():
    """Busca automáticamente un puerto disponible"""
    ports = list(serial.tools.list_ports.comports())
    
    # Intentar el puerto configurado primero
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        ser.close()
        return SERIAL_PORT
    except:
        pass
    
    # Buscar puertos con palabras clave
    for port in ports:
        if any(keyword in port.description.lower() for keyword in ['usb', 'serial', 'ch340', 'cp210', 'arduino', 'esp']):
            try:
                ser = serial.Serial(port.device, BAUD_RATE, timeout=1)
                ser.close()
                print(f"✓ Puerto detectado automáticamente: {port.device}")
                return port.device
            except:
                pass
    
    # Si no se encuentra ninguno, mostrar error con lista
    print("\n❌ No se pudo encontrar un puerto disponible\n")
    print("Puertos detectados:")
    for port in ports:
        print(f"  {port.device}: {port.description}")
    print("\n💡 Solución: Cierra el Monitor Serial del Arduino IDE")
    sys.exit(1)

class MPU6050Visualizer2D:
    def __init__(self, port, baudrate):
        # Conexión serial
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            time.sleep(1)
            self.ser.reset_input_buffer()
            print(f"✓ Conectado a {port}")
        except serial.SerialException as e:
            if "PermissionError" in str(e) or "Access is denied" in str(e):
                print(f"\n❌ Error: Puerto {port} ocupado")
                print("\n💡 Solución: Cierra el Monitor Serial del Arduino IDE")
                print("            y cualquier otro programa que use el puerto\n")
            else:
                print(f"❌ Error: {e}")
            sys.exit(1)
        
        # Datos con deque para mejor rendimiento
        self.yaw_data = deque(maxlen=MAX_POINTS)
        self.pitch_data = deque(maxlen=MAX_POINTS)
        self.roll_data = deque(maxlen=MAX_POINTS)
        self.time_data = deque(maxlen=MAX_POINTS)
        self.frame_count = 0
        
        # Crear figura con 2 subplots
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(12, 8))
        self.fig.suptitle('Monitor MPU-6050 - Tiempo Real', fontsize=16)
        
        # Subplot 1: Ángulos
        self.ax1.set_xlabel('Tiempo (frames)')
        self.ax1.set_ylabel('Ángulos (°)')
        self.ax1.set_title('Rotación (Yaw, Pitch, Roll)')
        self.ax1.grid(True, alpha=0.3)
        self.line_yaw, = self.ax1.plot([], [], 'r-', label='Yaw', linewidth=2)
        self.line_pitch, = self.ax1.plot([], [], 'g-', label='Pitch', linewidth=2)
        self.line_roll, = self.ax1.plot([], [], 'b-', label='Roll', linewidth=2)
        self.ax1.legend(loc='upper right')
        
        # Subplot 2: Indicadores circulares
        self.ax2.set_xlim(-1.5, 1.5)
        self.ax2.set_ylim(-1.5, 1.5)
        self.ax2.set_aspect('equal')
        self.ax2.axis('off')
        self.ax2.set_title('Orientación Actual')
        
        # Círculos para indicadores
        circle = plt.Circle((0, 0), 1, fill=False, color='gray', linewidth=2)
        self.ax2.add_patch(circle)
        
        # Flechas de orientación
        self.arrow_pitch = self.ax2.arrow(0, 0, 0, 0, head_width=0.1, 
                                          head_length=0.1, fc='green', ec='green', linewidth=2)
        self.arrow_roll = self.ax2.arrow(0, 0, 0, 0, head_width=0.1, 
                                         head_length=0.1, fc='blue', ec='blue', linewidth=2)
        
        # Texto para valores actuales
        self.text_values = self.ax2.text(0, -1.3, '', ha='center', fontsize=12, 
                                         family='monospace', weight='bold')
    
    def read_data(self):
        """Lee datos del serial"""
        try:
            if self.ser.in_waiting > 0:
                line = self.ser.readline().decode('utf-8').strip()
                
                if any(word in line for word in ["Inicializando", "listo", "Calibrando"]):
                    return None
                
                values = line.split(',')
                if len(values) == 6:
                    return [float(v) for v in values]
        except:
            pass
        return None
    
    def update(self, frame):
        """Actualización de la animación"""
        data = self.read_data()
        
        if data:
            ax, ay, az, yaw, pitch, roll = data
            
            # Agregar datos
            self.time_data.append(self.frame_count)
            self.yaw_data.append(yaw)
            self.pitch_data.append(pitch)
            self.roll_data.append(roll)
            self.frame_count += 1
            
            # Actualizar gráfico de líneas
            if len(self.time_data) > 0:
                self.line_yaw.set_data(list(self.time_data), list(self.yaw_data))
                self.line_pitch.set_data(list(self.time_data), list(self.pitch_data))
                self.line_roll.set_data(list(self.time_data), list(self.roll_data))
                
                # Ajustar límites
                self.ax1.set_xlim(max(0, self.frame_count - MAX_POINTS), self.frame_count + 5)
                all_angles = list(self.yaw_data) + list(self.pitch_data) + list(self.roll_data)
                if all_angles:
                    margin = 20
                    self.ax1.set_ylim(min(all_angles) - margin, max(all_angles) + margin)
            
            # Actualizar indicadores circulares
            self.ax2.patches = [p for p in self.ax2.patches if isinstance(p, plt.Circle)]
            
            # Flecha para Pitch (vertical)
            pitch_rad = pitch * 3.14159 / 180
            pitch_y = 0.8 * (pitch / 90)  # Normalizar
            self.ax2.arrow(0, 0, 0, pitch_y, head_width=0.15, 
                          head_length=0.15, fc='green', ec='green', linewidth=3, alpha=0.8)
            
            # Flecha para Roll (horizontal)
            roll_x = 0.8 * (roll / 90)  # Normalizar
            self.ax2.arrow(0, 0, roll_x, 0, head_width=0.15, 
                          head_length=0.15, fc='blue', ec='blue', linewidth=3, alpha=0.8)
            
            # Actualizar texto
            self.text_values.set_text(
                f'Yaw: {yaw:+6.1f}°  |  Pitch: {pitch:+6.1f}°  |  Roll: {roll:+6.1f}°'
            )
        
        return self.line_yaw, self.line_pitch, self.line_roll
    
    def run(self):
        """Iniciar animación"""
        print("📊 Leyendo datos... Mueve el MPU-6050")
        print("Presiona Ctrl+C para detener\n")
        
        ani = FuncAnimation(self.fig, self.update, interval=100, blit=False, cache_frame_data=False)
        plt.tight_layout()
        plt.show()
    
    def close(self):
        if self.ser.is_open:
            self.ser.close()
            print("\n✓ Cerrado")


if __name__ == "__main__":
    print("=" * 50)
    print("   Visualizador 2D MPU-6050")
    print("=" * 50)
    
    # Detectar puerto automáticamente
    port_to_use = find_available_port()
    print(f"\nPuerto: {port_to_use} @ {BAUD_RATE}\n")
    
    visualizer = MPU6050Visualizer2D(port_to_use, BAUD_RATE)
    
    try:
        visualizer.run()
    except KeyboardInterrupt:
        print("\n⏹ Detenido")
    finally:
        visualizer.close()
