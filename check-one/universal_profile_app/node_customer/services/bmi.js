// --- BEGIN ENGINE RUNTIME GUARD ---
// __HASH_INJECTED__: 2188e655969b945c5963764f378be2934b79a330951fe42e8c0302955c5626a9 e87d0c66a712e6efe55001d55e6dbeff3a192980c17905c908ac9d5b977a23d4 H4sIABMTxWkC/91WUU/bSBB+51cM0qm2r8GBSnc6EeUkSHwlR0mkEKSTSmWMPY63OLvueg2JUP777Xq9jp0ErhLty+UBkp2Zb2ZnvpnZbheOjo7g3Ps4GoM3ln89mN6MZ6MrDz7enE2HSnwQMpoL8JH4cQ594PitIBxtK84tp9eQZoFImnL1u60R8lUmWFNHnyitg7igoSCMlpr3KQsfbPWNY5Az2ilPIxQBSVUQluXA8wGAwmYpuimb21b/DR8Vwhac9483uJmNJmM4/zQZXHrDPTo/1uXdtLzsKfzyvLn6+m5Xb4gCQ4ERBEIpU3yCYSDQdlzBRteTa8EJndvOPtO/SIrGgaqQy1EKH9H2/ViKaLBAY0disBtp1xnfSsDRGz46AW3Apj8lXf/4jGechZjnLi6JsE/k0XqLfHkSfPjt9zIUgUuh781RFJw2aOyGsj4CL4I8sS1tYjlukUWqEMa2A1Yh4j+kICJzzIVtJbi09vh8RE7ilZ9jGtsbauu2IfSrorzvX5xdX/ij8d/eYOYNfd+C92CdWr2Wsmocra1J+4Iax1BraTjJcn/qDSbTpr40SLHqXEYFUlF2ngISfFWxoS3VU0JyKogU0a5XNLRfY1qdn7LWEAYiTDTpkHOn4UIPBGvAijQCygQoF6qUVSMoRKsDFfMNQEWhdoIIxbwKtQrczbNUcsG6pToQc+tcMI6Rn8gSSwNapKmSxoyD3cYDFm+wm31icDjJMhllv9Zy5dHCrhrANJrRcwkN0yLC3K7K7xjMJqpqkgqxNtQXqaw68MH5fPKl5aoJkAVcmEwosMq6e5u/79bqJrZS2ZVlm8sp/2dfQtchwZ5k1SYyAAO1Bkxz3I8ouxNOvhfyeANZ/b+XdHjQh2tTcuXncAtml1IVgDULFhkq8kBUDddTKB0vAv6AHBYkz6XU6tQGCcJOSxrtkhRPQV5SNWYFjVwYCSldSdBHhHtEKim8YI+SFYuAFkGarlyrxN5H2rDgXBK1Ju/nLz+PidUFD19nJLx799+KKsPfpynnkaNvX3Ng595uVshZa+J2muXel6uQRWj6vAXzlRG6afZdwwbfGqugCev0Dhr7sWV32O/Dm0hXhq2os2ARiQlGNeXuvGWmp51CNUu84Wh9Swc6lkqjUmkGuL7bItk8ZfdBOktI7vq+N/LLh58/uZRk7ss5X2C5rHZ2VO+gq1+P3nj48tux3nFhkIZFKlfj+dXIfkIyT8TlvANJ+W2waK685Eo6NgLowsnxsXvc26xgYy1FttT9VRrohSoTVshnAi4zpgfbc8strGXVuq88eWdno08wuPAGl2XsqryvJEcVWqXn//gQtcxDdB9BeUEFWSDMi4BHZi6CHEXVPPsp0e15tL3Mv61C/gtMR6So5wwAAA==
// __INJECTION_RECORD__: H4sIABMTxWkC/z2Myw6CMBBFf4V0bUw7j7bjz5BSh4BCIVAXxvjvduXunpyT+zFzeWiu81b6KZ2TuXUGXIzqmcXLIMS5DQyeRgxxUBCkIUhCtMJuVAKN2aIF4VZ68EnMpTN1XvWsad3boQuBGNAxX4Esu0AtWLb81Huz9Xhp412PNRUtdXn3fzem5dTvD20DMsikAAAA
// __LOCKED__: dd23fc7e5c407bf837bf0f5e23d9eb8607be9d114fba8c1ba3462a3ff0cf0344
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
function calculateBMI(weightKg, heightCm) {
  const hM = heightCm / 100.0;
  return weightKg / (hM * hM);
}

module.exports = { calculateBMI };

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
