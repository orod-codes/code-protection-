using System;
using ProfileApp.Models;

namespace ProfileApp.Utils {
    public static class ConsoleUtil {
        public static User ReadUser() {
            Console.Write("Enter name: ");
            string name = Console.ReadLine();
            Console.Write("Enter age: ");
            int age = int.Parse(Console.ReadLine());
            Console.Write("Enter weight (kg): ");
            double w = double.Parse(Console.ReadLine());
            Console.Write("Enter height (cm): ");
            double h = double.Parse(Console.ReadLine());
            return new User {
                Name = name,
                Age = age,
                Weight = w,
                Height = h
            };
        }
    }
}
