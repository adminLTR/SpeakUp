#include "Simple_MPU6050.h"
#define MPU6050_DEFAULT_ADDRESS 0x68 

class Gyroscope
{
private:
    Simple_MPU6050* mpu;
    
    float yaw;
    float pitch;
    float roll;

    float ax, ay, ax;
    float gx, gy, gz;

    void read_values(int16_t*, int16_t*, int32_t*);
public:
    Gyroscope();
    ~Gyroscope();
    void begin();
    void read();
};

Gyroscope::Gyroscope() {}

Gyroscope::begin() {
    this->mpu->begin();
    this->mpu->Set_DMP_Output_Rate_Hz(10); 
    this->mpu->CalibrateMPU();
    this->mpu->load_DMP_Image();
    this->mpu->on_FIFO(this->read_values);
}

Gyroscope::read_values(int16_t *gyro, int16_t *accel, int32_t *quat) {
    Quaternion q;
    VectorFloat gravity;
    float ypr[3] = { 0, 0, 0 };
    float xyz[3] = { 0, 0, 0 };
    this->mpu->GetQuaternion(&q, quat);
    this->mpu->GetGravity(&gravity, &q);
    this->mpu->GetYawPitchRoll(ypr, &q, &gravity);
    this->mpu->ConvertToDegrees(ypr, xyz);
    
    this->Yaw = xyz[0];
    this->Pitch = xyz[1];
    this->Roll = xyz[2];
    this->ax = accel[0];
    this->ay = accel[1];
    this->az = accel[2];
    this->gx = gyro[0];
    this->gy = gyro[1];
    this->gz = gyro[2];
}

Gyroscope::read() {
    static unsigned long FIFO_DelayTimer;
    if ((millis() - FIFO_DelayTimer) >= (99)) { 
        if( mpu.dmp_read_fifo(false)) FIFO_DelayTimer= millis() ; 
    }
}

Gyroscope::~Gyroscope() {}
