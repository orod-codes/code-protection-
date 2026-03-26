function greet(name, timeOfDay = "day") {
    if (!name || typeof name !== "string") {
      throw new Error("Invalid name provided.");
    }
  
    return `Good ${timeOfDay}, ${name}!`;
  }
  
  function getTimeOfDay() {
    const hour = new Date().getHours();
  
    if (hour < 12) return "morning";
    if (hour < 18) return "afternoon";
    return "evening";
  }
  
  function main() {
    try {
      const user = "JS Customer";
      const timeOfDay = getTimeOfDay();
  
      const message = greet(user, timeOfDay);
      console.log(message);
  
      console.log("Current time:", new Date().toLocaleString());
    } catch (error) {
      console.error("Something went wrong:", error.message);
    }
  }
  
  main();