import java.util.Scanner;
import model.User;
import service.BMIService;
import util.InputUtil;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        User user = InputUtil.readUser(sc);
        double bmi = BMIService.calculate(user.weight, user.height);
        System.out.println("Hello " + user.name + ", age " + user.age + ", BMI: " + bmi);
        sc.close();
    }
}
