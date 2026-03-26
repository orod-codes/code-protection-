const readline = require('readline');
const { User } = require('../models/user');

function createRl() {
  return readline.createInterface({ input: process.stdin, output: process.stdout });
}

function question(rl, q) {
  return new Promise((resolve) => rl.question(q, resolve));
}

async function readUser(rl) {
  const name = (await question(rl, 'Enter name: ')).trim();
  const age = parseInt(await question(rl, 'Enter age: '), 10);
  const weight = parseFloat(await question(rl, 'Enter weight (kg): '));
  const height = parseFloat(await question(rl, 'Enter height (cm): '));
  return new User(name, age, weight, height);
}

module.exports = { createRl, readUser };
