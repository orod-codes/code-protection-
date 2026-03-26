def bmi_status(bmi_value: float) -> str:
    if bmi_value < 18.5:
        return "Underweight"
    if bmi_value < 25:
        return "Normal"
    if bmi_value < 30:
        return "Overweight"
    return "Obese"
