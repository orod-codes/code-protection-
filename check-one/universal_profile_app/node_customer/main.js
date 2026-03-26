// --- BEGIN ENGINE RUNTIME GUARD ---
// __HASH_INJECTED__: e2c5affe963dc50d56661473ed74f320a5d2c2a9252ff3f7651adb258b2d6c2f dbf1dde0bb26a8667bc1a7d135f4f1337a450c1d8fb804cb6223a04d2a071997 H4sIABMTxWkC/91WbW/bNhD+nl/BAEMloY68FNgwJPCAxNYaL60DOA4woCkURjrZbGhSIyknRuD/vqMoyfJL0wJpv8wfEpu8e+5499xLt0uOjo7IefR+OCLRCP9GZHwzmgw/RuT9zdl4YK8PEim0ITGwONOkRxT8WzAFvpdpLzht3ebUzNr39vemRKKWuZFtGXdipQ6yQiSGSVFK3nOZPPj2mwKqpeiUpykYyrh1wvMC8nxAiMWWHEIup77Xe8XHurAFF/0T9W8mw6sROf9w1b+MBntkfqzJu3H52BPyy/P66au7XbkBGEgMpIQaKyzgkQyoAT8IjRxeX10bxcTUD/ap/sU41AZshkIFeLkAP44zvBJ0DrUey4jfCruL+FYAjl7xcQHYBGzbs7erHx/xXMkEtA7hiRn/GI9WW+TTM/rut99LVww8GfduBaZQokXjMMH8GLigeuZ7TsULwiJPbSJq3Q7xCpP9gRcpm4I2vjeDJ2+PzQUoli1jDTzz19R2ZcPEF0v5OL44u76Ih6O/o/4kGsSxR94S78Q73RC2heOkHWm/IqYgcVIODlkej6P+1bgtjwocqsqVwoAwZeVZIKOWFRs2b12XQE7R1BLteikS/yWmNfEpc00SapKZIx0oFbRMuIbg9WXBUyKkIdaETWVVCBbR65CK+TVARaHNADEBunK1cjzUOUcueLfCOVK/WhupII1nmGJUEAXn9jaTivibeERma+x2ndQ4iuU5etlrpEI8mvtVAdSFVsuFTCS8SEH7VfqDGrONaoukQmwU3UMqrQ55F3w6/rxhqg2QU2XqSFiwSrt7q992G/Hat1I4xLRNscv/2UPoxiWyJ1iNCjpQQ60IcA37EbE6yfH3Qv66hqz+3yMdHtzhqk65tXO4BbNLqQrAm9B5DpY8JK2a6wkpDc+pegBF5kxrvPU6jcIMyE5J1tIlKR6pLqmayUKkIRkavF0i6ALIPYBACs/lAlkxp6KgnC9Dr8TeR9qkUAqJ2pD30+efx8TqgYcvM5K8efNtQRvh75PEfhS41zcc2Hl3mBfYa2u/g3a698UqkSnUdb4B80UysS72XcUW31qjoA0bnB605uOG3mGvR15FutJtS525TFnGIG0odxc95a7bWdR6iLcMrW5F3/lSSVQibQdXd1skm3J5T/lkxnQYx9EwLhe/+OoSydzDPl9AOax2ZtTpQddtj9Fo8K3d8RkbO08KjpPx/OMQ+0BrAwy7GtSC4UTu3s/Zel9EnXK+jnmn7PU3KLatWRhcE7rM7Y9U47AhzVCdU0xye5Iq2yxrTMf39RRzIoW10SP0kTLTGPUVb+0phqCXFqj1IN/qhY/ApjMc+OWPWfljz35zdwGcS8xLKWZn4KpD6BTqE/yKBwhq04umqlVshQNO2B5R+at4mHCpwa/yiBlyD8ZAdF/Y6idnww+kfxH1L8v0WAa/kH/LZcuA/+Ou7dW79r4aVIUwbA5kWlCV1q2fYLetWvZP8W7PXvr1EttK5H/2r+q4yg0AAA==
// __INJECTION_RECORD__: H4sIABMTxWkC/z2MQQ6DMAzAvoJ6niaaNi3sMyg0iWCDgqAcpml/X087Wrb8MXN+SirzloeJzsk8GiOQkFSlD44TtowhBOujE45eHbSEDAmoBwRVpzGgJR4BuxE4JFBza0yZVzkLrXsd2hg9grOId3A9+NjVYNnSS7jaclxSeZdjpSy5LO/h75SWU74/8zkKcKQAAAA=
// __LOCKED__: 449857a02969cee68f49b9d2952b256160411e240f6342059ff0b164255044b6
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
