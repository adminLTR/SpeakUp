#include "KalmanFilter.h"

class Finger
{
private:
    int pin;
    KalmanFilter* filter;
public:
    Finger(int pin) {
        this->pin = pin;
        this->filter = new KalmanFilter(1.0, 0.0, 1.0, 0.01, 0.5, 0.0, 1.0);
    }
    int read() {
        int r = analogRead(this->pin);
        return (int)this->filter->filter((float)r);
    }
    ~Finger() {
        delete this->filter;
    }
};

