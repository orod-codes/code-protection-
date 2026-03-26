from models.user_profile import UserProfile
from services.validator import parse_float, parse_int, require_text


class ProfileCollector:
    @staticmethod
    def collect() -> UserProfile:
        name = require_text(input("Enter name: "), "Name")
        age = parse_int(input("Enter age: "), "Age")
        phone = require_text(input("Enter phone number: "), "Phone")
        weight_kg = parse_float(input("Enter weight (kg): "), "Weight")
        height_cm = parse_float(input("Enter height (cm): "), "Height")
        email = require_text(input("Enter email: "), "Email")
        city = require_text(input("Enter city: "), "City")
        gender = require_text(input("Enter gender: "), "Gender")

        return UserProfile(
            name=name,
            age=age,
            phone=phone,
            weight_kg=weight_kg,
            height_cm=height_cm,
            email=email,
            city=city,
            gender=gender,
        )
