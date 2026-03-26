#include <iostream>
#include <string>
#include "BMI.h"
#include "User.h"

int main() {
    User u;
    std::cout << "Enter name: ";
    std::getline(std::cin, u.name);

    std::cout << "Enter age: ";
    std::cin >> u.age;

    std::cout << "Enter weight (kg): ";
    std::cin >> u.weight;

    std::cout << "Enter height (cm): ";
    std::cin >> u.height;

    double bmi = calculateBMI(u.weight, u.height);
    std::cout << "Hello " << u.name << ", age " << u.age << ", BMI: " << bmi << std::endl;
    return 0;
}
