function calculateBMI(weightKg, heightCm) {
  const hM = heightCm / 100.0;
  return weightKg / (hM * hM);
}

module.exports = { calculateBMI };
