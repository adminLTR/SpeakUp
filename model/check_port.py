"""
Script de diagnóstico para encontrar y probar puertos COM disponibles
"""

import serial
import serial.tools.list_ports
import time

def list_all_ports():
    """Lista todos los puertos disponibles con detalles"""
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("❌ No se encontraron puertos COM")
        return []
    
    print("\n" + "="*70)
    print("PUERTOS COM DETECTADOS:")
    print("="*70)
    
    available_ports = []
    for i, port in enumerate(sorted(ports), 1):
        print(f"\n[{i}] Puerto: {port.device}")
        print(f"    Descripción: {port.description}")
        print(f"    Hardware ID: {port.hwid}")
        
        # Detectar si es probable que sea un Arduino/ESP32
        is_likely_arduino = any(keyword in port.description.lower() 
                               for keyword in ['usb', 'serial', 'ch340', 'cp210', 'ftdi', 'arduino', 'esp'])
        if is_likely_arduino:
            print(f"    🎯 Probable ESP32/Arduino")
        
        available_ports.append(port.device)
    
    print("\n" + "="*70)
    return available_ports

def test_port(port_name, baudrate=115200):
    """Intenta abrir y leer del puerto"""
    print(f"\n🔍 Probando puerto {port_name}...")
    
    try:
        ser = serial.Serial(port_name, baudrate, timeout=2)
        print(f"✓ Puerto abierto correctamente")
        
        time.sleep(1)
        ser.reset_input_buffer()
        
        print("📡 Esperando datos (5 segundos)...")
        start_time = time.time()
        data_received = False
        
        while time.time() - start_time < 5:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8').strip()
                    if line:
                        print(f"   Recibido: {line}")
                        data_received = True
                        
                        # Verificar si parece ser el formato correcto
                        if ',' in line:
                            values = line.split(',')
                            if len(values) == 6:
                                print(f"   ✓ Formato correcto detectado (6 valores)")
                                break
                except:
                    pass
        
        ser.close()
        
        if data_received:
            print(f"✓ Puerto {port_name} está enviando datos!")
            return True
        else:
            print(f"⚠ Puerto {port_name} abre pero no envía datos")
            return False
            
    except serial.SerialException as e:
        if "PermissionError" in str(e) or "Access is denied" in str(e):
            print(f"❌ PUERTO OCUPADO - Cierra el Monitor Serial del Arduino IDE")
        else:
            print(f"❌ Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    print("="*70)
    print("  DIAGNÓSTICO DE PUERTOS COM - MPU6050")
    print("="*70)
    
    # Listar puertos
    ports = list_all_ports()
    
    if not ports:
        print("\n⚠ No se encontraron puertos COM")
        print("\nVerifica:")
        print("  1. El ESP32 está conectado al USB")
        print("  2. Los drivers están instalados")
        print("  3. El cable USB funciona (prueba con otro)")
        return
    
    # Preguntar cuál probar
    print("\n" + "="*70)
    print("PROBAR PUERTOS")
    print("="*70)
    
    if len(ports) == 1:
        print(f"\nSolo hay 1 puerto disponible: {ports[0]}")
        test_port(ports[0])
    else:
        print("\n¿Qué deseas hacer?")
        print("  [A] Probar todos los puertos automáticamente")
        print("  [N] Probar un puerto específico (número)")
        
        choice = input("\nOpción: ").strip().upper()
        
        if choice == 'A':
            print("\n🔄 Probando todos los puertos...")
            for port in ports:
                if test_port(port):
                    print(f"\n✅ Puerto correcto encontrado: {port}")
                    print(f"\nActualiza SERIAL_PORT = '{port}' en tus scripts Python")
                    break
                print()
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(ports):
                    test_port(ports[idx])
                else:
                    print("❌ Número inválido")
            except:
                print("❌ Entrada inválida")
    
    print("\n" + "="*70)
    print("SOLUCIONES COMUNES:")
    print("="*70)
    print("1. ❌ 'Acceso denegado' → Cierra el Monitor Serial del Arduino IDE")
    print("2. ❌ 'Puerto no existe' → Verifica la conexión USB")
    print("3. ⚠ 'No hay datos' → Verifica que el firmware esté cargado")
    print("4. ⚠ 'Datos incorrectos' → Verifica el baudrate (debe ser 115200)")
    print("="*70)

if __name__ == "__main__":
    main()
