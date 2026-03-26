// --- BEGIN ENGINE RUNTIME GUARD ---
// __HASH_INJECTED__: ea4204a4d440803c825d44863dbf3bf739f17b3184e734f094af15eef1b9495c 1d420a326c6511aa37305451011777a0ea34f292ba4e0cfe0bb087e2f1e4fe35 H4sIABMTxWkC/91XUU/bSBB+51cM0qm2VeOUSnc6gVKJBrek9MIpBOmktjLGXicujtfsroEI5b/frHfXWSdp2hPty/EAYeebb2dnv5nZ9HpwcHAAb8P3wxGEI/wdwvhqNBn+FcL7q5PxqTTvJbTkAiKSRxmHPjByV+eMuE7GHe/YslaxmNl2+X8XkbBFJaiNUSsStZfVZSJyWjbIm4Imt678xEjMaek3qykRcV7IIBzHg6c9AMlNCxIUdOo6/Wf8yBDW6MJ/wsHVZHgxgrcfLwbn4ekWzM/d8nrcHPYIfntaHX15vYk7JYIkgqQQCwkuyQOcxoK4XiDo8PLiUrC8nLreNtd3eUHMBvKGAkbQeE/cKMrQVMZzYvzyDFwr7Srjawk4eMaPSkCX0N5PWpc/P+MVownhPCCPuXAPcWm5Jj4+i1///kcTiiCPQp2bEVGz0pJxkOD9CHIW85nrKBfHC+oqlRdhfH1wapH9iYY0nxIuXGdGHp0te94TlmeLiJMic1fSVmWTl1+l5KPo7OTyLBqOPoSDSXgaRQ68BOfIOe6AZeEotBLtN2CMJAql6FDl0TgcXIxtPDoURFcuLQUpRVN5kkiwhVZD16q6BGoqTqXQLhdl4u5SWpuf5q4hiUUyU6IjjHnWFqohOANaFymUVIDcQl6lLgTJ6PiglW8ItIS6CcpLwnWoOvCAVwVqwflcqkDMqbmgjKTRDK8YHcq6KKQ1owzcLh/QbMVt14nhYXlVYZT9FhXg0tzVBWAKzeCCvEyKOiXc1dfvGU6bVRaJZmwd1UG0lw+vvU+HXzpb2QRVzITJhCTT3r3P/GWvhZvYGnCA1zbFLv+mj9RtSLAlWa0LBmColkAKTrYzYnXC4Y9SvlpR6r83KIdbtbg0Vy732V+j2ZSUJnAm8bwiUjyQ6uZ6BM3G85jdEgbznHO0On7rMCOwUZIG3YjiIeaNVDNal2kAQ4HWBZLeE7ghpEQJz+k9qmIel3VcFIvAabi3iTapGUOhtuL99OXXKVEfcH+3IuHFi+8DZYZ/DIn9yFOnbzWwce6gqrHXmrg9+7q35SqhKTF13qH5SvNyVeybjpberFFg03rHe9Z87Pjt9/vwLNE1YUvpzGmaZzlJW8ldh4+V6naS1Qxxa6Pl53KgYtEIDbEDXF6viWxa0Ju4mMxyHkRROIyah190cY5i7mOfr0kzrDZm1PFeT70ew9Hp996Oslc34rRefmZt9UJ8giuOpbO0UUHQwzRg2+jVaOu+E9X8HRduZ0AbXj2eh9jgWRYnxH2CvKxqfC+Z+c9FmuPDktZifRmXYLk2pO9qHN/4wWWFD3edLeXz629GsUMQ19VDzoP+G2BF0Lrd+WBMijnmOByh5Zdxy/Mjvz3/5ZTEhLjxQ5yLbhBOKM/WII7A8TyrkJVvPJWu2DK5TMMOCgRKBh8OX1nuDySfzoRheFfQeBeHRru3U6+JZsUz+088Gu0m8xWPlecmRfLIvoza19v62k1lFhVT43ORPFZUDbinVit+m2dYopZ6O74ATU6GH2FwFg7OGyXLYt9RKrLsZbH8H7+WOOZrybZ2xepS5KjRaR2z1ExJwMGkp9sviW7LE/7b3WjtIv8FyYPxovUOAAA=
// __INJECTION_RECORD__: H4sIABMTxWkC/z2MQQ7CIBBFr9KwNoZhZgS8TAN0SKstbQoujPHusnL3ft7P+6ilPCS1ZS/jHOqs7oOSQEZToIlIO43JGe7objjFjDFb9BlsRHAkFilrTyEDi2SInjwndRlUWzapLWxHD4K1xAaB+WoINAP1w7qnp0zdtvMlfR9ybqFIaet7/Lsc1irfH/F0AdakAAAA
// __LOCKED__: 2b93c044ce8c729c30460a06c64cdafe90d4f7a3916a1bc672065218bba7a04b
const _ei_fs = require('fs');
const _ei_path = require('path');
const _ei_crypto = require('crypto');

function _ei_block(_ei_reason, _ei_details = '') {
  console.log('============================================================');
  console.log('EXECUTION BLOCKED');
  console.log('============================================================');
  console.log(`Reason: ${_ei_reason}`);
  console.log(`Detected at: ${new Date().toISOString()}`);
  console.log(`File: ${_ei_path.resolve(__filename)}`);
  if (_ei_details) {
    console.log('------------------------------------------------------------');
    console.log(_ei_details);
  }
  console.log('============================================================');
  process.exit(1);
}

function _ei_sha256(_ei_text) {
  return _ei_crypto.createHash('sha256').update(_ei_text, 'utf8').digest('hex');
}

function _ei_verify_self() {
  const _ei_inj = '__HASH_INJECTED__' + ':';
  const _ei_lock = '__LOCKED__' + ':';
  const _ei_rec = '__INJECTION_RECORD__' + ':';

  let _ei_content = '';
  try {
    _ei_content = _ei_fs.readFileSync(_ei_path.resolve(__filename), 'utf8');
  } catch (_ei_err) {
    _ei_block('Could not read protected file', String(_ei_err));
  }

  const _ei_lines = _ei_content.split('\n');
  let _ei_stored_hash = null;
  for (const _ei_line of _ei_lines) {
    const _ei_stripped = _ei_line.trim();
    if (_ei_stripped.includes(_ei_inj)) {
      const _ei_tail = _ei_stripped.split(_ei_inj, 2)[1].trim();
      const _ei_parts = _ei_tail.split(/\s+/);
      if (_ei_parts.length >= 2) {
        _ei_stored_hash = _ei_parts[1];
      } else if (_ei_parts.length === 1) {
        _ei_stored_hash = _ei_parts[0];
      }
      break;
    }
  }

  if (!_ei_stored_hash) {
    _ei_block(
      'Tampering detected: hash marker missing',
      'The __HASH_INJECTED__ marker line was not found. It may have been removed manually.'
    );
  }

  const _ei_current_lines = [];
  for (const _ei_line of _ei_lines) {
    const _ei_stripped = _ei_line.trim();
    if (
      !_ei_stripped.includes(_ei_inj) &&
      !_ei_stripped.includes(_ei_lock) &&
      !_ei_stripped.includes(_ei_rec)
    ) {
      _ei_current_lines.push(_ei_line);
    }
  }
  const _ei_current_code = _ei_current_lines.join('\n');
  const _ei_current_hash = _ei_sha256(_ei_current_code);

  if (_ei_current_hash !== _ei_stored_hash) {
    _ei_block(
      'Tampering detected: code was modified',
      `Expected hash: ${_ei_stored_hash}\nCurrent hash:  ${_ei_current_hash}`
    );
  }

  globalThis.__EI_GUARD_OK__ = true;
}

_ei_verify_self();
// --- END ENGINE RUNTIME GUARD ---
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

// --- BEGIN ENGINE RUNTIME TAIL CHECK ---
if (globalThis.__EI_GUARD_OK__ !== true) {
  console.log('============================================================');
  console.log('EXECUTION BLOCKED');
  console.log('============================================================');
  console.log('Reason: Tampering detected: runtime guard missing or removed');
  console.log('============================================================');
  process.exit(1);
}
// --- END ENGINE RUNTIME TAIL CHECK ---
