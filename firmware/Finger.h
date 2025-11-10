class Finger
{
private:
    int pin;
public:
    Finger(int);
    ~Finger();
    int read();
};

Finger::Finger(int pin)
{
    this->pin = pin;
}

Finger::~Finger() {}

int Finger::read() {
    return analogRead(this->pin);
}