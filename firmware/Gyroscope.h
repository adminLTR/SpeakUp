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
    
    // Filtro de media móvil simple
    static const int FILTER_SIZE = 5;
    float ax_buffer[FILTER_SIZE];
    float ay_buffer[FILTER_SIZE];
    float az_buffer[FILTER_SIZE];
    int buffer_index;
    
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
    buffer_index = 0;
    
    // Inicializar buffers
    for(int i = 0; i < FILTER_SIZE; i++) {
        ax_buffer[i] = 0;
        ay_buffer[i] = 0;
        az_buffer[i] = 0;
    }
}

void Gyroscope::begin() {
    // ESP32 Devkit V1: SDA = GPIO 21, SCL = GPIO 22 (pines por defecto)
    Wire.begin(21, 22);
    Wire.setClock(400000);
    
    delay(100);
    mpu.initialize();
    
    // Esperar hasta que el MPU6050 se conecte
    Serial.println("Buscando MPU6050...");
    while (!mpu.testConnection()) {
        Serial.println("MPU6050 no detectado. Reintentando...");
        delay(2000);
        mpu.initialize();
    }
    
    Serial.println("MPU6050 conectado!");
    
    // Configurar rangos
    mpu.setFullScaleGyroRange(MPU6050_GYRO_FS_250);
    mpu.setFullScaleAccelRange(MPU6050_ACCEL_FS_2);
    
    Serial.println("MPU6050 inicializado correctamente");
    lastTime = millis();
}

void Gyroscope::read() {
    int16_t ax_raw, ay_raw, az_raw;
    int16_t gx_raw, gy_raw, gz_raw;
    
    // Leer valores crudos
    mpu.getMotion6(&ax_raw, &ay_raw, &az_raw, &gx_raw, &gy_raw, &gz_raw);
    
    // Convertir aceleración a g's
    float ax_temp = ax_raw / 16384.0;
    float ay_temp = ay_raw / 16384.0;
    float az_temp = az_raw / 16384.0;
    
    // Aplicar filtro de media móvil
    ax_buffer[buffer_index] = ax_temp;
    ay_buffer[buffer_index] = ay_temp;
    az_buffer[buffer_index] = az_temp;
    buffer_index = (buffer_index + 1) % FILTER_SIZE;
    
    // Calcular promedio
    ax = ay = az = 0;
    for(int i = 0; i < FILTER_SIZE; i++) {
        ax += ax_buffer[i];
        ay += ay_buffer[i];
        az += az_buffer[i];
    }
    ax /= FILTER_SIZE;
    ay /= FILTER_SIZE;
    az /= FILTER_SIZE;
    
    // Convertir giroscopio a grados/segundo
    gx = gx_raw / 131.0;
    gy = gy_raw / 131.0;
    gz = gz_raw / 131.0;
    
    // Calcular delta de tiempo
    unsigned long currentTime = millis();
    dt = (currentTime - lastTime) / 1000.0;
    lastTime = currentTime;
    
    if(dt > 0) {
        // Calcular ángulos usando acelerómetro
        float accelPitch = atan2(ay, sqrt(ax * ax + az * az)) * 180.0 / PI;
        float accelRoll = atan2(-ax, az) * 180.0 / PI;
        
        // Filtro complementario mejorado
        pitch = 0.96 * (pitch + gy * dt) + 0.04 * accelPitch;
        roll = 0.96 * (roll + gx * dt) + 0.04 * accelRoll;
        yaw += gz * dt;
    }
}

Gyroscope::~Gyroscope() {
    // Destructor vacío
}
