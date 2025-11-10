"""
Visualizador 3D de movimiento y rotación del MPU-6050
Lee datos del puerto serial en formato: x,z,yaw,pitch,roll
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
SERIAL_PORT = 'COM14'  # Cambia esto según tu puerto (COM3, COM4, etc. en Windows)
BAUD_RATE = 115200


def list_available_ports():
    """Lista todos los puertos seriales disponibles"""
    ports = serial.tools.list_ports.comports()
    available_ports = []
    print("\nPuertos seriales detectados:")
    for port, desc, hwid in sorted(ports):
        print(f"  {port}: {desc}")
        available_ports.append(port)
    return available_ports


def find_arduino_port():
    """Intenta encontrar automáticamente el puerto del Arduino"""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        # Buscar puertos que contengan palabras clave de Arduino
        if 'Arduino' in port.description or 'CH340' in port.description or 'USB' in port.description:
            return port.device
    return None

class MPU6050Visualizer:
    def __init__(self, port, baudrate):
        """Inicializa el visualizador y la conexión serial"""
        try:
            # Configurar el puerto serial sin resetear el ESP32
            self.ser = serial.Serial()
            self.ser.port = port
            self.ser.baudrate = baudrate
            self.ser.timeout = 1
            self.ser.dtr = False  # No resetear con DTR
            self.ser.rts = False  # No resetear con RTS
            self.ser.open()
            
            print(f"✓ Conectado a {port} a {baudrate} baudios")
            
            # Esperar y limpiar buffer
            time.sleep(0.5)
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            
            print("✓ Esperando datos del sensor...")
            
        except serial.SerialException as e:
            print(f"\n❌ Error al conectar con el puerto serial: {e}")
            print("\n💡 Posibles soluciones:")
            print("   1. Cierra el Monitor Serial del Arduino IDE")
            print("   2. Desconecta y reconecta el ESP32")
            print("   3. Verifica que el puerto sea el correcto")
            print("   4. Intenta con otro puerto de la lista\n")
            list_available_ports()
            sys.exit(1)
        
        # Datos del sensor
        self.x_data = []
        self.z_data = []
        self.yaw_data = []
        self.pitch_data = []
        self.roll_data = []
        
        # Configuración de la figura
        self.fig = plt.figure(figsize=(14, 6))
        self.ax1 = self.fig.add_subplot(121, projection='3d')
        self.ax2 = self.fig.add_subplot(122)
        
        # Título
        self.fig.suptitle('Visualización de Movimiento MPU-6050', fontsize=16)
        
        # Configurar el subplot 3D
        self.ax1.set_xlabel('X (g)')
        self.ax1.set_ylabel('Z (g)')
        self.ax1.set_zlabel('Y (g)')
        self.ax1.set_title('Posición y Orientación 3D')
        self.ax1.set_xlim([-2, 2])
        self.ax1.set_ylim([-2, 2])
        self.ax1.set_zlim([-2, 2])
        
        # Configurar el subplot 2D para ángulos
        self.ax2.set_xlabel('Tiempo (frames)')
        self.ax2.set_ylabel('Ángulos (grados)')
        self.ax2.set_title('Ángulos de Rotación')
        self.ax2.grid(True)
        
        # Líneas para los ángulos
        self.line_yaw, = self.ax2.plot([], [], 'r-', label='Yaw', linewidth=2)
        self.line_pitch, = self.ax2.plot([], [], 'g-', label='Pitch', linewidth=2)
        self.line_roll, = self.ax2.plot([], [], 'b-', label='Roll', linewidth=2)
        self.ax2.legend()
        
        # Trayectoria en 3D
        self.trajectory_line, = self.ax1.plot([], [], [], 'c-', alpha=0.5, linewidth=1)
        
        # Cubo para representar el objeto
        self.cube = None
        
        # Contador de frames
        self.frame_count = 0
        self.max_points = 100  # Máximo de puntos a mostrar en el gráfico
    
    def create_cube(self, size=0.3):
        """Crea los vértices de un cubo centrado en el origen"""
        s = size / 2
        vertices = np.array([
            [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s],  # cara inferior
            [-s, -s, s], [s, -s, s], [s, s, s], [-s, s, s]       # cara superior
        ])
        return vertices
    
    def rotate_vertices(self, vertices, yaw, pitch, roll):
        """Rota los vértices según los ángulos de Euler (en grados)"""
        # Convertir a radianes
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
        
        # Aplicar rotaciones: R = Rz * Ry * Rx
        R = Rz @ Ry @ Rx
        
        # Rotar cada vértice
        rotated = vertices @ R.T
        return rotated
    
    def get_cube_faces(self, vertices):
        """Define las caras del cubo para dibujar"""
        faces = [
            [vertices[0], vertices[1], vertices[2], vertices[3]],  # inferior
            [vertices[4], vertices[5], vertices[6], vertices[7]],  # superior
            [vertices[0], vertices[1], vertices[5], vertices[4]],  # frontal
            [vertices[2], vertices[3], vertices[7], vertices[6]],  # trasera
            [vertices[0], vertices[3], vertices[7], vertices[4]],  # izquierda
            [vertices[1], vertices[2], vertices[6], vertices[5]]   # derecha
        ]
        return faces
    
    def read_sensor_data(self):
        """Lee una línea del puerto serial y extrae los valores"""
        try:
            if self.ser.in_waiting > 0:
                line = self.ser.readline().decode('utf-8').strip()
                
                # Saltar líneas de inicialización y debug
                if ("Inicializando" in line or "listo" in line or "inicializado" in line or
                    "Buscando" in line or "detectado" in line or "conectado" in line or
                    "MPU" in line or line == ""):
                    return None
                
                # Parsear datos: x,z,yaw,pitch,roll
                values = line.split(',')
                if len(values) == 5:
                    x = float(values[0])
                    z = float(values[1])
                    yaw = float(values[2])
                    pitch = float(values[3])
                    roll = float(values[4])
                    return x, z, yaw, pitch, roll
        except (ValueError, UnicodeDecodeError, IndexError) as e:
            pass  # Ignorar líneas malformadas
        
        return None
    
    def update(self, frame):
        """Función de actualización para la animación"""
        data = self.read_sensor_data()
        
        if data is not None:
            x, z, yaw, pitch, roll = data
            
            # Guardar datos
            self.x_data.append(x)
            self.z_data.append(z)
            self.yaw_data.append(yaw)
            self.pitch_data.append(pitch)
            self.roll_data.append(roll)
            self.frame_count += 1
            
            # Limitar el número de puntos
            if len(self.x_data) > self.max_points:
                self.x_data.pop(0)
                self.z_data.pop(0)
                self.yaw_data.pop(0)
                self.pitch_data.pop(0)
                self.roll_data.pop(0)
            
            # Actualizar trayectoria 3D
            y_data = [0] * len(self.x_data)  # Y en el espacio 3D (altura)
            self.trajectory_line.set_data(self.x_data, self.z_data)
            self.trajectory_line.set_3d_properties(y_data)
            
            # Actualizar cubo en la posición actual
            if self.cube:
                self.cube.remove()
            
            # Crear y rotar el cubo
            cube_vertices = self.create_cube(size=0.4)
            rotated_vertices = self.rotate_vertices(cube_vertices, yaw, pitch, roll)
            
            # Trasladar el cubo a la posición actual
            if len(self.x_data) > 0:
                current_x = self.x_data[-1]
                current_z = self.z_data[-1]
                rotated_vertices[:, 0] += current_x
                rotated_vertices[:, 1] += current_z
            
            # Dibujar el cubo
            faces = self.get_cube_faces(rotated_vertices)
            self.cube = Poly3DCollection(faces, alpha=0.7, facecolors='cyan', 
                                        edgecolors='black', linewidths=2)
            self.ax1.add_collection3d(self.cube)
            
            # Actualizar gráfico de ángulos
            time_data = list(range(len(self.yaw_data)))
            self.line_yaw.set_data(time_data, self.yaw_data)
            self.line_pitch.set_data(time_data, self.pitch_data)
            self.line_roll.set_data(time_data, self.roll_data)
            
            # Ajustar límites del gráfico de ángulos
            if len(time_data) > 0:
                self.ax2.set_xlim(0, max(len(time_data), 10))
                all_angles = self.yaw_data + self.pitch_data + self.roll_data
                if all_angles:
                    min_angle = min(all_angles)
                    max_angle = max(all_angles)
                    margin = 10
                    self.ax2.set_ylim(min_angle - margin, max_angle + margin)
        
        return self.trajectory_line, self.line_yaw, self.line_pitch, self.line_roll
    
    def run(self):
        """Inicia la animación"""
        print("Leyendo datos del sensor... Mueve el MPU-6050")
        print("Presiona Ctrl+C para detener")
        
        ani = FuncAnimation(self.fig, self.update, interval=50, blit=False)
        plt.tight_layout()
        plt.show()
    
    def close(self):
        """Cierra la conexión serial sin resetear el ESP32"""
        if self.ser and self.ser.is_open:
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self.ser.close()
            print("\n✓ Conexión serial cerrada correctamente")


if __name__ == "__main__":
    print("=" * 50)
    print("   Visualizador 3D MPU-6050 - SpeakUp Project")
    print("=" * 50)
    
    print(f"\n→ Usando puerto: {SERIAL_PORT}")
    print(f"→ Baudrate: {BAUD_RATE}")
    print("\n" + "=" * 50 + "\n")
    
    visualizer = MPU6050Visualizer(SERIAL_PORT, BAUD_RATE)
    
    try:
        visualizer.run()
    except KeyboardInterrupt:
        print("\n\n⏹ Deteniendo visualización...")
    finally:
        visualizer.close()
