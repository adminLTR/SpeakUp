#include <MPU6050.h>
#include <Wire.h>

class Gyroscope
{
private:
    MPU6050 mpu;
    
    float yaw;
    float pitch;
    float roll;

    float ax, ay, az;
    float gx, gy, gz;

    // Variables para el cálculo de ángulos
    unsigned long lastTime;
    float dt;
    
public:
    Gyroscope();
    ~Gyroscope();
    void begin();
    void read();
    
    // Métodos para obtener los valores
    float getYaw() { return yaw; }
    float getPitch() { return pitch; }
    float getRoll() { return roll; }
    float getAccelX() { return ax; }
    float getAccelY() { return ay; }
    float getAccelZ() { return az; }
    float getGyroX() { return gx; }
    float getGyroY() { return gy; }
    float getGyroZ() { return gz; }
};

Gyroscope::Gyroscope() {
    yaw = pitch = roll = 0;
    ax = ay = az = 0;
    gx = gy = gz = 0;
    lastTime = 0;
    dt = 0;
}

void Gyroscope::begin() {
    // ESP32 Feather V2: SDA = GPIO 22 (Pin 22), SCL = GPIO 20 (Pin 20)
    // Inicializar I2C en los pines por defecto del ESP32 Feather V2
    Wire.begin(22, 20); // SDA, SCL
    Wire.setClock(400000); // Velocidad I2C a 400kHz (Fast Mode)
    
    mpu.initialize();
    
    // Esperar hasta que el MPU6050 se conecte
    Serial.println("Buscando MPU6050...");
    while (!mpu.testConnection()) {
        Serial.println("MPU6050 no detectado. Reintentando en 2 segundos...");
        delay(2000);
        mpu.initialize(); // Reintentar inicialización
    }
    
    Serial.println("MPU6050 conectado!");
    
    // Configurar rangos
    mpu.setFullScaleGyroRange(MPU6050_GYRO_FS_250);  // ±250°/s
    mpu.setFullScaleAccelRange(MPU6050_ACCEL_FS_2);  // ±2g
    
    Serial.println("MPU6050 inicializado correctamente");
    lastTime = millis();
}

void Gyroscope::read() {
    int16_t ax_raw, ay_raw, az_raw;
    int16_t gx_raw, gy_raw, gz_raw;
    
    // Leer valores crudos
    mpu.getMotion6(&ax_raw, &ay_raw, &az_raw, &gx_raw, &gy_raw, &gz_raw);
    
    // Convertir aceleración a g's (±2g range, 16384 LSB/g)
    ax = ax_raw / 16384.0;
    ay = ay_raw / 16384.0;
    az = az_raw / 16384.0;
    
    // Convertir giroscopio a grados/segundo (±250°/s range, 131 LSB/°/s)
    gx = gx_raw / 131.0;
    gy = gy_raw / 131.0;
    gz = gz_raw / 131.0;
    
    // Calcular delta de tiempo
    unsigned long currentTime = millis();
    dt = (currentTime - lastTime) / 1000.0; // Convertir a segundos
    lastTime = currentTime;
    
    // Calcular ángulos usando acelerómetro (en grados)
    float accelPitch = atan2(ay, sqrt(ax * ax + az * az)) * 180.0 / PI;
    float accelRoll = atan2(-ax, az) * 180.0 / PI;
    
    // Integrar giroscopio para obtener ángulos (filtro complementario)
    pitch = 0.98 * (pitch + gy * dt) + 0.02 * accelPitch;
    roll = 0.98 * (roll + gx * dt) + 0.02 * accelRoll;
    yaw += gz * dt; // El yaw solo puede calcularse con giroscopio
}

Gyroscope::~Gyroscope() {
    // Destructor vacío
}