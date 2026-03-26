namespace ProfileApp.Services {
    public static class BMIService {
        public static double Calculate(double weightKg, double heightCm) {
            double hM = heightCm / 100.0;
            return weightKg / (hM * hM);
        }
    }
}
