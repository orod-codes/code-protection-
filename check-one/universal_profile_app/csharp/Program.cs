using System;
using ProfileApp.Models;
using ProfileApp.Services;
using ProfileApp.Utils;

class Program {
    static void Main() {
        User user = ConsoleUtil.ReadUser();
        double bmi = BMIService.Calculate(user.Weight, user.Height);
        Console.WriteLine("Hello " + user.Name + ", age " + user.Age + ", BMI: " + bmi);
    }
}
