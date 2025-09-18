class Finger
{
private:
    int pin;
public:
    Finger(int);
    ~Finger();
};

Finger::Finger(int pin)
{
    this->pin = pin;
}

Finger::~Finger() {}