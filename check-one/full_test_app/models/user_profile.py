from dataclasses import dataclass


@dataclass
class UserProfile:
    name: str
    age: int
    phone: str
    weight_kg: float
    height_cm: float
    email: str
    city: str
    gender: str

    def bmi(self) -> float:
        height_m = self.height_cm / 100.0
        if height_m <= 0:
            return 0.0
        return self.weight_kg / (height_m * height_m)
