#include "Finger.h"
#include "Gyroscope.h"

// left hand
Finger left_index(A0);  
Finger left_middle(A1); 
Finger left_ring(A2);   
Finger left_pinky(A3);   
Finger left_thumb(A4);

// Gyroscope
Gyroscope gyro;

void setup() {
  Serial.begin(115200);
  
  // Inicializar el giroscopio
  Serial.println("Inicializando MPU-6050...");
  gyro.begin();
  Serial.println("MPU-6050 listo!");
  delay(1000);
}

void loop() {
  // Leer datos del giroscopio
  gyro.read();
  
  // Formato: x,z,yaw,pitch,roll
  Serial.print(gyro.getAccelX()); Serial.print(",");
  Serial.print(gyro.getAccelZ()); Serial.print(",");
  Serial.print(gyro.getYaw()); Serial.print(",");
  Serial.print(gyro.getPitch()); Serial.print(",");
  Serial.println(gyro.getRoll());
  
  delay(10);
}