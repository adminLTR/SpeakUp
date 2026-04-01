

/**
 * @file KalmanFilter.h
 * @brief 1D Kalman Filter implementation for sensor filtering
 * @details This class implements a one-dimensional Kalman filter optimized
 *          for embedded systems. It is ideal for filtering sensor signals
 *          such as accelerometers and gyroscopes (MPU6050).
 * 
 * Kalman Filter equations:
 * - Prediction:  x_pred = F * x + B * u
 *                P_pred = F * P * F + Q
 * - Update:      K = P_pred * H / (H * P_pred * H + R)
 *                x = x_pred + K * (z - H * x_pred)
 *                P = (1 - K * H) * P_pred
 */
class KalmanFilter
{
private:
    // Model parameters (scalars for 1D filter)
    float F;   // State transition factor (typically 1.0 for simple systems)
    float B;   // Control input factor (0.0 if no external control)
    float H;   // Measurement factor (typically 1.0, relates state to measurement)
    
    // Noise covariances
    float Q;   // Process noise covariance (adjusts confidence in the model)
    float R;   // Measurement noise covariance (adjusts confidence in the sensor)
    
    // Filter state
    float x;   // Current state estimate
    float P;   // Current error covariance estimate

public:
    /**
     * @brief Kalman Filter constructor
     * @param F State transition factor (use 1.0 for static systems)
     * @param B Control input factor (use 0.0 if no control)
     * @param H Measurement factor (use 1.0 for direct state measurement)
     * @param Q Process noise covariance (typical values: 0.001 - 0.1)
     *          High values = more reactive to changes, less smoothing
     * @param R Measurement noise covariance (typical values: 0.1 - 10)
     *          High values = more smoothing, less reactive
     * @param x0 Initial state (can be the first measurement)
     * @param P0 Initial error covariance (typical values: 1.0)
     * 
     * @example For filtering gyroscope data:
     *          KalmanFilter gyroFilter(1.0, 0.0, 1.0, 0.01, 0.5, 0.0, 1.0);
     */
    KalmanFilter(float F, float B, float H, float Q, float R, float x0, float P0) {
        this->F = F;
        this->B = B;
        this->H = H;
        this->Q = Q;
        this->R = R;
        this->x = x0;
        this->P = P0;
    }

    /**
     * @brief Kalman Filter prediction step
     * @param u Control input (use 0.0 if no external control)
     * @details Predicts the next state based on the system model.
     *          This step increases uncertainty (P) according to process noise (Q).
     */
    void predict(float u = 0.0) {
        // State prediction: x_pred = F * x + B * u
        this->x = this->F * this->x + this->B * u;
        
        // Covariance prediction: P_pred = F * P * F + Q
        this->P = this->F * this->P * this->F + this->Q;
    }

    /**
     * @brief Kalman Filter update step
     * @param z Sensor measurement
     * @details Corrects the prediction using the sensor measurement.
     *          Calculates Kalman gain (K) which balances between
     *          prediction and measurement based on their uncertainties.
     */
    void update(float z) {
        // Kalman gain: K = P * H / (H * P * H + R)
        float K = this->P * this->H / (this->H * this->P * this->H + this->R);
        
        // State update: x = x + K * (z - H * x)
        // (z - H * x) is the innovation (difference between measurement and prediction)
        this->x = this->x + K * (z - this->H * this->x);
        
        // Covariance update: P = (1 - K * H) * P
        this->P = (1.0 - K * this->H) * this->P;
    }

    /**
     * @brief Applies a complete filtering cycle (predict + update)
     * @param z Sensor measurement
     * @param u Control input (optional, default 0.0)
     * @return Filtered state
     * @details Convenient method that combines predict() and update() in one call.
     *          Use this method when processing real-time measurements.
     */
    float filter(float z, float u = 0.0) {
        predict(u);
        update(z);
        return this->x;
    }

    /**
     * @brief Gets the current estimated state
     * @return Current state estimate
     */
    float getState() const {
        return this->x;
    }

    /**
     * @brief Gets the current error covariance
     * @return Current uncertainty estimate
     */
    float getCovariance() const {
        return this->P;
    }

    /**
     * @brief Resets the filter with new initial values
     * @param x0 New initial state
     * @param P0 New initial covariance
     */
    void reset(float x0, float P0) {
        this->x = x0;
        this->P = P0;
    }

    /**
     * @brief Adjusts the filter noise parameters
     * @param Q New process noise covariance
     * @param R New measurement noise covariance
     * @details Use this to dynamically adjust the filter response
     */
    void setNoise(float Q, float R) {
        this->Q = Q;
        this->R = R;
    }

    /**
     * @brief Destructor
     */
    ~KalmanFilter() {}
};