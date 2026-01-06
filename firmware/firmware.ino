#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

Adafruit_MPU6050 mpu;

// Filtro de media móvil
const int FILTER_SIZE = 10;
float ax_buffer[FILTER_SIZE], ay_buffer[FILTER_SIZE], az_buffer[FILTER_SIZE];
float gx_buffer[FILTER_SIZE], gy_buffer[FILTER_SIZE], gz_buffer[FILTER_SIZE];
int buffer_index = 0;
bool buffer_filled = false;

// Variables para ángulos
float yaw = 0, pitch = 0, roll = 0;
unsigned long lastTime = 0;

// Zona muerta para eliminar ruido pequeño
const float ACCEL_DEADZONE = 0.02;  // m/s^2
const float GYRO_DEADZONE = 0.01;   // rad/s

float applyDeadzone(float value, float deadzone) {
  if (abs(value) < deadzone) return 0;
  return value;
}

void setup(void) {
  Serial.begin(115200);
  while (!Serial) delay(10);

  Serial.println("Inicializando MPU6050...");

  if (!mpu.begin()) {
    Serial.println("MPU6050 no detectado!");
    while (1) delay(10);
  }

  // Configuración optimizada
  mpu.setAccelerometerRange(MPU6050_RANGE_2_G);
  mpu.setGyroRange(MPU6050_RANGE_250_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  Serial.println("MPU6050 listo!");
  
  // Inicializar buffers
  for(int i = 0; i < FILTER_SIZE; i++) {
    ax_buffer[i] = ay_buffer[i] = az_buffer[i] = 0;
    gx_buffer[i] = gy_buffer[i] = gz_buffer[i] = 0;
  }
  
  // Calibración inicial
  Serial.println("Calibrando (no muevas el sensor)...");
  for(int i = 0; i < 50; i++) {
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);
    delay(20);
  }
  
  Serial.println("Listo para enviar datos");
  lastTime = millis();
  delay(500);
}

void loop() {
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  // Aplicar zona muerta
  float ax = applyDeadzone(a.acceleration.x, ACCEL_DEADZONE);
  float ay = applyDeadzone(a.acceleration.y, ACCEL_DEADZONE);
  float az = applyDeadzone(a.acceleration.z, ACCEL_DEADZONE);
  float gx = applyDeadzone(g.gyro.x, GYRO_DEADZONE);
  float gy = applyDeadzone(g.gyro.y, GYRO_DEADZONE);
  float gz = applyDeadzone(g.gyro.z, GYRO_DEADZONE);

  // Guardar en buffer circular
  ax_buffer[buffer_index] = ax;
  ay_buffer[buffer_index] = ay;
  az_buffer[buffer_index] = az;
  gx_buffer[buffer_index] = gx;
  gy_buffer[buffer_index] = gy;
  gz_buffer[buffer_index] = gz;
  
  buffer_index = (buffer_index + 1) % FILTER_SIZE;
  if (buffer_index == 0) buffer_filled = true;

  // Calcular promedio (filtro de media móvil)
  int samples = buffer_filled ? FILTER_SIZE : buffer_index + 1;
  float ax_avg = 0, ay_avg = 0, az_avg = 0;
  float gx_avg = 0, gy_avg = 0, gz_avg = 0;
  
  for(int i = 0; i < samples; i++) {
    ax_avg += ax_buffer[i];
    ay_avg += ay_buffer[i];
    az_avg += az_buffer[i];
    gx_avg += gx_buffer[i];
    gy_avg += gy_buffer[i];
    gz_avg += gz_buffer[i];
  }
  
  ax_avg /= samples;
  ay_avg /= samples;
  az_avg /= samples;
  gx_avg /= samples;
  gy_avg /= samples;
  gz_avg /= samples;

  // Calcular ángulos
  unsigned long currentTime = millis();
  float dt = (currentTime - lastTime) / 1000.0;
  lastTime = currentTime;

  if(dt > 0 && dt < 1) {  // Validar delta tiempo razonable
    // Convertir aceleración a g's (viene en m/s^2, dividir por 9.81)
    float ax_g = ax_avg / 9.81;
    float ay_g = ay_avg / 9.81;
    float az_g = az_avg / 9.81;
    
    // Calcular ángulos desde acelerómetro
    float accelPitch = atan2(ay_g, sqrt(ax_g * ax_g + az_g * az_g)) * 180.0 / PI;
    float accelRoll = atan2(-ax_g, az_g) * 180.0 / PI;
    
    // Convertir giroscopio de rad/s a grados/s
    float gx_deg = gx_avg * 180.0 / PI;
    float gy_deg = gy_avg * 180.0 / PI;
    float gz_deg = gz_avg * 180.0 / PI;
    
    // Filtro complementario
    pitch = 0.96 * (pitch + gy_deg * dt) + 0.04 * accelPitch;
    roll = 0.96 * (roll + gx_deg * dt) + 0.04 * accelRoll;
    yaw += gz_deg * dt;
  }

  // Formato: ax,ay,az,yaw,pitch,roll (compatible con visualizadores)
  Serial.print(ax_avg / 9.81, 2);  // Convertir a g's
  Serial.print(",");
  Serial.print(ay_avg / 9.81, 2);
  Serial.print(",");
  Serial.print(az_avg / 9.81, 2);
  Serial.print(",");
  Serial.print(yaw, 1);
  Serial.print(",");
  Serial.print(pitch, 1);
  Serial.print(",");
  Serial.println(roll, 1);

  delay(50);  // 20Hz
}