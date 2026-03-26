from models.user_profile import UserProfile
from utils.formatters import bmi_status


def print_profile(profile: UserProfile) -> None:
    bmi_value = profile.bmi()

    print("\n" + "=" * 42)
    print("USER PROFILE REPORT")
    print("=" * 42)
    print(f"Name      : {profile.name}")
    print(f"Age       : {profile.age}")
    print(f"Phone     : {profile.phone}")
    print(f"Email     : {profile.email}")
    print(f"City      : {profile.city}")
    print(f"Gender    : {profile.gender}")
    print(f"Weight    : {profile.weight_kg:.1f} kg")
    print(f"Height    : {profile.height_cm:.1f} cm")
    print(f"BMI       : {bmi_value:.2f} ({bmi_status(bmi_value)})")
    print("=" * 42)
