const { calculateBMI } = require('./services/bmi');
const { createRl, readUser } = require('./utils/io');

async function main() {
  const rl = createRl();
  try {
    const user = await readUser(rl);
    const bmi = calculateBMI(user.weight, user.height);
    console.log(`Hello ${user.name}, age ${user.age}, BMI: ${bmi}`);
  } finally {
    rl.close();
  }
}

main();
