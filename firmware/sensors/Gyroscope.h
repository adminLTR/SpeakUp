#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

#include "KalmanFilter.h"

class Gyroscope
{
private:
    Adafruit_MPU6050 mpu;
    sensors_event_t a, g, temp;
    KalmanFilter* filterAccX;
    KalmanFilter* filterAccY;
    KalmanFilter* filterAccZ;
    KalmanFilter* filterGyroX;
    KalmanFilter* filterGyroY;
    KalmanFilter* filterGyroZ;
    
public:
    Gyroscope() {}
    ~Gyroscope() {}
    
    void begin() {
        if (!mpu.begin()){
            while (1) {
                delay(10);
            }
        }
        mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
        mpu.setGyroRange(MPU6050_RANGE_500_DEG);
        mpu.setFilterBandwidth(MPU6050_BAND_5_HZ);
        this->filterAccX = new KalmanFilter(1.0, 0.0, 1.0, 0.01, 0.5, 0.0, 1.0);
        this->filterAccY = new KalmanFilter(1.0, 0.0, 1.0, 0.01, 0.5, 0.0, 1.0);
        this->filterAccZ = new KalmanFilter(1.0, 0.0, 1.0, 0.01, 0.5, 0.0, 1.0);
        this->filterGyroX = new KalmanFilter(1.0, 0.0, 1.0, 0.01, 0.5, 0.0, 1.0);
        this->filterGyroY = new KalmanFilter(1.0, 0.0, 1.0, 0.01, 0.5, 0.0, 1.0);
        this->filterGyroZ = new KalmanFilter(1.0, 0.0, 1.0, 0.01, 0.5, 0.0, 1.0);
    }
    void read() {
        mpu.getEvent(&a, &g, &temp);
    }
    float getAccelerationX() {
        return this->filterAccX->filter(a.acceleration.x);
    }
    float getAccelerationY() {
        return this->filterAccY->filter(a.acceleration.y);
    }
    float getAccelerationZ() {
        return this->filterAccZ->filter(a.acceleration.z);
    }
    float getGyroX() {
        return this->filterGyroX->filter(g.gyro.x);
    }
    float getGyroY() {
        return this->filterGyroY->filter(g.gyro.y);
    }
    float getGyroZ() {
        return this->filterGyroZ->filter(g.gyro.z);
    }
};
