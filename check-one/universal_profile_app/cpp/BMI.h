#ifndef BMI_H
#define BMI_H

inline double calculateBMI(double weightKg, double heightCm) {
    double hM = heightCm / 100.0;
    return weightKg / (hM * hM);
}

#endif
