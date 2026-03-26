package service;

public class BMIService {
    public static double calculate(double weightKg, double heightCm) {
        double hM = heightCm / 100.0;
        return weightKg / (hM * hM);
    }
}
