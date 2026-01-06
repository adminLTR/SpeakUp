"""
Visualizador 3D de movimiento y rotación del MPU-6050
Lee datos del puerto serial en formato: ax,ay,az,yaw,pitch,roll
y muestra una animación 3D del objeto en movimiento.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import serial
import serial.tools.list_ports
import sys
import time

# Configuración del puerto serial
SERIAL_PORT = 'COM8'  # Cambia esto según tu puerto
BAUD_RATE = 115200


def list_available_ports():
    """Lista todos los puertos seriales disponibles"""
    ports = serial.tools.list_ports.comports()
    print("\nPuertos seriales detectados:")
    for port, desc, hwid in sorted(ports):
        print(f"  {port}: {desc}")

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
                print(f"✓ Puerto detectado: {port.device}")
                return port.device
            except:
                pass
    
    print("\n❌ No se pudo encontrar un puerto disponible")
    list_available_ports()
    print("\n💡 Cierra el Monitor Serial del Arduino IDE\n")
    sys.exit(1)

class MPU6050Visualizer:
    def __init__(self, port, baudrate):
        """Inicializa el visualizador y la conexión serial"""
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            time.sleep(1)
            self.ser.reset_input_buffer()
            print(f"✓ Conectado a {port}")
        except serial.SerialException as e:
            if "PermissionError" in str(e):
                print(f"\n❌ Puerto {port} ocupado")
                print("\n💡 Cierra el Monitor Serial del Arduino IDE\n")
            else:
                print(f"\n❌ Error: {e}")
                list_available_ports()
            sys.exit(1)
        
        # Datos del sensor
        self.yaw_data = []
        self.pitch_data = []
        self.roll_data = []
        
        # Configuración simplificada
        self.fig = plt.figure(figsize=(12, 6))
        self.ax1 = self.fig.add_subplot(121, projection='3d')
        self.ax2 = self.fig.add_subplot(122)
        
        self.fig.suptitle('Visualización MPU-6050', fontsize=14)
        
        # Subplot 3D
        self.ax1.set_xlabel('X')
        self.ax1.set_ylabel('Y')
        self.ax1.set_zlabel('Z')
        self.ax1.set_title('Orientación 3D')
        self.ax1.set_xlim([-1, 1])
        self.ax1.set_ylim([-1, 1])
        self.ax1.set_zlim([-1, 1])
        
        # Subplot ángulos
        self.ax2.set_xlabel('Frames')
        self.ax2.set_ylabel('Ángulos (°)')
        self.ax2.set_title('Rotación')
        self.ax2.grid(True, alpha=0.3)
        
        self.line_yaw, = self.ax2.plot([], [], 'r-', label='Yaw', linewidth=1.5)
        self.line_pitch, = self.ax2.plot([], [], 'g-', label='Pitch', linewidth=1.5)
        self.line_roll, = self.ax2.plot([], [], 'b-', label='Roll', linewidth=1.5)
        self.ax2.legend()
        
        self.cube = None
        self.frame_count = 0
        self.max_points = 50
    
    def create_cube(self, size=0.5):
        """Crea los vértices de un cubo"""
        s = size / 2
        vertices = np.array([
            [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s],
            [-s, -s, s], [s, -s, s], [s, s, s], [-s, s, s]
        ])
        return vertices
    
    def rotate_vertices(self, vertices, yaw, pitch, roll):
        """Rota los vértices según los ángulos de Euler"""
        yaw_rad = np.radians(yaw)
        pitch_rad = np.radians(pitch)
        roll_rad = np.radians(roll)
        
        # Matriz de rotación en X (Roll)
        Rx = np.array([
            [1, 0, 0],
            [0, np.cos(roll_rad), -np.sin(roll_rad)],
            [0, np.sin(roll_rad), np.cos(roll_rad)]
        ])
        
        # Matriz de rotación en Y (Pitch)
        Ry = np.array([
            [np.cos(pitch_rad), 0, np.sin(pitch_rad)],
            [0, 1, 0],
            [-np.sin(pitch_rad), 0, np.cos(pitch_rad)]
        ])
        
        # Matriz de rotación en Z (Yaw)
        Rz = np.array([
            [np.cos(yaw_rad), -np.sin(yaw_rad), 0],
            [np.sin(yaw_rad), np.cos(yaw_rad), 0],
            [0, 0, 1]
        ])
        
        R = Rz @ Ry @ Rx
        rotated = vertices @ R.T
        return rotated
    
    def get_cube_faces(self, vertices):
        """Define las caras del cubo"""
        faces = [
            [vertices[0], vertices[1], vertices[2], vertices[3]],
            [vertices[4], vertices[5], vertices[6], vertices[7]],
            [vertices[0], vertices[1], vertices[5], vertices[4]],
            [vertices[2], vertices[3], vertices[7], vertices[6]],
            [vertices[0], vertices[3], vertices[7], vertices[4]],
            [vertices[1], vertices[2], vertices[6], vertices[5]]
        ]
        return faces
    
    def read_sensor_data(self):
        """Lee una línea del puerto serial"""
        try:
            if self.ser.in_waiting > 0:
                line = self.ser.readline().decode('utf-8').strip()
                
                if any(word in line for word in ["Inicializando", "listo", "Calibrando", "detectado"]):
                    return None
                
                values = line.split(',')
                if len(values) == 6:
                    return [float(v) for v in values]
        except:
            pass
        return None
    
    def update(self, frame):
        """Actualización optimizada"""
        data = self.read_sensor_data()
        
        if data:
            ax, ay, az, yaw, pitch, roll = data
            
            self.yaw_data.append(yaw)
            self.pitch_data.append(pitch)
            self.roll_data.append(roll)
            self.frame_count += 1
            
            # Limitar puntos
            if len(self.yaw_data) > self.max_points:
                self.yaw_data.pop(0)
                self.pitch_data.pop(0)
                self.roll_data.pop(0)
            
            # Actualizar cubo 3D
            if self.cube:
                self.cube.remove()
            
            cube_vertices = self.create_cube()
            rotated = self.rotate_vertices(cube_vertices, yaw, pitch, roll)
            faces = self.get_cube_faces(rotated)
            self.cube = Poly3DCollection(faces, alpha=0.7, facecolors='cyan', 
                                        edgecolors='navy', linewidths=1.5)
            self.ax1.add_collection3d(self.cube)
            
            # Actualizar gráfico de ángulos
            time_data = list(range(len(self.yaw_data)))
            self.line_yaw.set_data(time_data, self.yaw_data)
            self.line_pitch.set_data(time_data, self.pitch_data)
            self.line_roll.set_data(time_data, self.roll_data)
            
            if time_data:
                self.ax2.set_xlim(0, max(len(time_data), 10))
                all_angles = self.yaw_data + self.pitch_data + self.roll_data
                if all_angles:
                    margin = 20
                    self.ax2.set_ylim(min(all_angles) - margin, max(all_angles) + margin)
        
        return self.line_yaw, self.line_pitch, self.line_roll
    
    def run(self):
        """Inicia la animación optimizada"""
        print("📊 Leyendo datos... Mueve el MPU-6050")
        print("Presiona Ctrl+C para detener\n")
        
        ani = FuncAnimation(self.fig, self.update, interval=100, blit=False, cache_frame_data=False)
        plt.tight_layout()
        plt.show()
    
    def close(self):
        """Cierra la conexión serial"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("\n✓ Cerrado")


if __name__ == "__main__":
    port_to_use = find_available_port()
    print(f"\n→ Usando puerto: {port_to_use}")
    print(f"→ Baudrate: {BAUD_RATE}")
    print("\n" + "=" * 50 + "\n")
    
    visualizer = MPU6050Visualizer(port_to_use
    print(f"→ Baudrate: {BAUD_RATE}")
    print("\n" + "=" * 50 + "\n")
    
    visualizer = MPU6050Visualizer(SERIAL_PORT, BAUD_RATE)
    
    try:
        visualizer.run()
    except KeyboardInterrupt:
        print("\n\n⏹ Deteniendo visualización...")
    finally:
        visualizer.close()
