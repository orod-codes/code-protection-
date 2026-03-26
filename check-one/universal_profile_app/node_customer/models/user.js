// --- BEGIN ENGINE RUNTIME GUARD ---
// __HASH_INJECTED__: 16c5a283ab39e088c42d6433a30fc301ad425352617232f9c9105f060a77f181 17b56e03b6a6fa70bbb3d5233565bdac7c25a796e2794c09798ad807f954c712 H4sIABMTxWkC/91WbW/bNhD+nl/BAEMloY68FNgwxPCA1NYaL50NOA4woCkURTpZbGRSI6nERuD/vqMoyvJLvQJpvywfbIf33MPj3XNHdrvk7OyMvA8+jMYkGONnQKa349nor4B8uL2cDrX5JOZMKhICDVNJ+kTAPyUV4DqpdLxey1pEKmvb9f/biFisCsXbGLOiUSdpyWJFOauQDzmPH139S0AkOetUqwmoiOY6CMfxyMsJIZqb5+DnfO46/Vf86RB26IK/g8HtbDQZk/cfJ4PrYHgA8323vJ9Wh70gP71sjr6+38cNQUGsICGR0mAGz2QYKXA9X/HRzeRGCcrmrnfI9Q+ag91AV8gXgMYncMMwRROLFmD9aErcVtpNxncScPaKP5OAbcL2ftq6/v4ZLwSPQUofllS557i03hGfzKJ3v/xahaJgqcy5BahSsJaM/Rjro+AqkpnrGBfH88si0YWwvh3ilCr9DQ0JnYNUrpPB0jmw5xMImq5CCXnqbqRt2oayL1ryYXh1eXMVjsZ/BoNZMAxDh7wlzoXT2wLrxjFoI9qvwATEBmXoUOXhNBhMpm08OuRQdy5nCpiqOk8TKbGq1bBtNVMCNRUlWmg3Kxa7x5TW5KeqNYkjFWdGdCCE19rCDARnwMs8IYwrorfQpawbQTM6HVIr3xLUEtpOEGUg61DrwH1Z5KgF546ZQOyppeICkjDDEqMDK/NcW1MuiLvNR3i64W73ieURtCgwyn6D8nFp4dYNYBvN4nzK4rxMQLp1+T3L2WbVTVIzNo7mILVXh7zzPp1/3tqqTVBEQtlMaLLau3sn33YbuI2tAvtYtjlO+d/7SN2ERA4kq3HBACzVmkAu4TAjdic5/1bKnzeU9fcDyuHRLK5tyfU+pzs0+5KqCZxZtChAi4ck9XC9INXGi0g8giALKiVanU7jkAHZa0mLrkTxHMlKqikvWeKTkULrCkmfgDwAMJTwgj+hKhYRK6M8X/lOxX1ItHEpBAq1Ee+nzz9OifUBT48rkrx5899AneFvQ+I88szpGw3sndsvSpy1Nm6vXe5DuYp5ArbPt2i+cMo2zb7v2NJb6ypo03q9k9b9uOV32u+TV4muCltLZ8ETmlJIGsndB8vCTDvNai/x1kbrOzYwsdSIGtIOcH2/I7J5zh+ifJZR6YdhMAqrh184uUYx93HOl1BdVnt3VO+ka16PwXh45O2YR1KSW4kt0dxpoowxZFfP/w6J5vjxDHSe4V2ZVd82XUqHpFF69uJXb7OKXriIn601Q4LL5kfLkllL1ljW+kyY4BKfFbAsuBmELybSNVa3e+RpPLscfSSDq2BwXZ1Ry+BIErUgdBr/jw9Wxz5YDwlZlExRrN68jERi5yfBkVXPvR8S3YHH3dd1ulPIfwFc1zB+Dw0AAA==
// __INJECTION_RECORD__: H4sIABMTxWkC/z3MSQ7CMAxA0atUWSMU23EGLlOZ1FELndSGBULcnaxYfj3pf8y0PjTXaVv7Uc7R3DoDPrNgJLlTUhtjdjh4RyRkSyYLMjhkYvQQkLCknMBysd5KCAUimEtn6rToWWXZ2xBCcIwEzFeklJCbz1t+6tCwHi9tveuxyKprnd/934rMp35/TUMMQ6MAAAA=
// __LOCKED__: 68affe82b28676947c5d2ddd504a1cbf723611e8bc155115a3fa10c8ce2e3e14
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
class User {
  constructor(name, age, weight, height) {
    this.name = name;
    this.age = age;
    this.weight = weight;
    this.height = height;
  }
}

module.exports = { User };

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
