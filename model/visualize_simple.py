"""
Visualizador SIMPLE en consola - MUY RÁPIDO
Muestra barras de progreso en la terminal para cada valor del MPU-6050
"""

import serial
import serial.tools.list_ports
import sys
import time
import os

SERIAL_PORT = 'COM8'  # Se autodetectará si no está disponible
BAUD_RATE = 115200

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
    print("\nPuertos detectados:")
    for port in ports:
        print(f"  {port.device}: {port.description}")
    print("\n💡 Cierra el Monitor Serial del Arduino IDE\n")
    sys.exit(1)

def clear_console():
    """Limpia la consola"""
    os.system('cls' if os.name == 'nt' else 'clear')

def create_bar(value, min_val=-2, max_val=2, length=40):
    """Crea una barra de progreso visual"""
    # Normalizar el valor entre 0 y 1
    normalized = (value - min_val) / (max_val - min_val)
    normalized = max(0, min(1, normalized))  # Limitar entre 0 y 1
    
    filled_length = int(length * normalized)
    bar = '█' * filled_length + '░' * (length - filled_length)
    return bar

def create_angle_bar(angle, length=40):
    """Crea una barra para ángulos (-180 a 180)"""
    # Normalizar el ángulo
    normalized = (angle + 180) / 360
    normalized = max(0, min(1, normalized))
    
    filled_length = int(length * normalized)
    center = length // 2
    
    bar = '░' * length
    bar_list = list(bar)
    bar_list[center] = '|'  # Marca el centro
    
    if filled_length < center:
        for i in range(filled_length, center):
            bar_list[i] = '◄'
    else:
        for i in range(center, filled_length):
            bar_list[i] = '►'
    
    return ''.join(bar_list)

def main():
    print("=" * 60)
    print("   Visualizador Simple MPU-6050 - SpeakUp Project")
    print("=" * 60)
    
    port_to_use = find_available_port()
    print(f"\nConectando a {port_to_use} @ {BAUD_RATE} baudios...")
    
    try:
        ser = serial.Serial(port_to_use, BAUD_RATE, timeout=1)
        time.sleep(1)
        ser.reset_input_buffer()
        print("✓ Conectado! Presiona Ctrl+C para salir\n")
        time.sleep(1)
        
        frame_count = 0
        last_update = time.time()
        fps = 0
        
        while True:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8').strip()
                    
                    # Saltar líneas de debug
                    if any(word in line for word in ["Inicializando", "listo", "Calibrando", "detectado"]):
                        continue
                    
                    # Parsear: ax,ay,az,yaw,pitch,roll
                    values = line.split(',')
                    if len(values) == 6:
                        ax, ay, az = float(values[0]), float(values[1]), float(values[2])
                        yaw, pitch, roll = float(values[3]), float(values[4]), float(values[5])
                        
                        # Calcular FPS
                        frame_count += 1
                        current_time = time.time()
                        if current_time - last_update >= 1.0:
                            fps = frame_count / (current_time - last_update)
                            frame_count = 0
                            last_update = current_time
                        
                        # Limpiar y mostrar
                        clear_console()
                        
                        print("=" * 60)
                        print("   MONITOR MPU-6050 EN TIEMPO REAL")
                        print("=" * 60)
                        print(f"FPS: {fps:.1f} | Presiona Ctrl+C para salir\n")
                        
                        print("📊 ACELERACIÓN (g):")
                        print(f"  X: {create_bar(ax)} {ax:+.2f}")
                        print(f"  Y: {create_bar(ay)} {ay:+.2f}")
                        print(f"  Z: {create_bar(az)} {az:+.2f}")
                        
                        print("\n🔄 ROTACIÓN (grados):")
                        print(f"  Yaw:   {create_angle_bar(yaw, 50)} {yaw:+6.1f}°")
                        print(f"  Pitch: {create_angle_bar(pitch, 50)} {pitch:+6.1f}°")
                        print(f"  Roll:  {create_angle_bar(roll, 50)} {roll:+6.1f}°")
                        
                        print("\n" + "=" * 60)
                        
                except ValueError:
                    pass  # Ignorar líneas malformadas
        if "PermissionError" in str(e):
            print(f"\n❌ Puerto ocupado")
            print("\n💡 Cierra el Monitor Serial del Arduino IDE\n")
        else:
            print(f"\n❌ Error: {e}")
            print("\nPuertos disponibles:")
            for port in serial.tools.list_ports.comports():
            print("\nPuertos disponibles:")
        for port in serial.tools.list_ports.comports():
            print(f"  {port.device}: {port.description}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹ Detenido por el usuario")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("✓ Puerto serial cerrado")

if __name__ == "__main__":
    main()
