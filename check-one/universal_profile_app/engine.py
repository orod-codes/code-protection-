#!/usr/bin/env python3
"""
Hash Injection Engine - Consolidated

This engine injects a hash code into the application file.
Once injected, it cannot inject again - the system detects
existing injections and blocks further attempts.

Process:
1. Check if valid hash already exists
2. If exists → stop (block injection)
3. If not → inject hash and lock it

This file consolidates all engine functionality:
- Hash computation (SHA-256)
- CRC computation
- HMAC computation
- Manifest management
- Integrity verification
- Scoring system
- Runtime monitoring
- Decoy memory traps
"""

import hashlib
import hmac
import zlib
import secrets
import json
import os
import sys
import shutil
import threading
import time
import random
import base64
import gzip
from typing import Optional, Dict, Tuple, Callable, List


# ============================================================================
# Hash Injection Engine
# ============================================================================

# Marker tokens (language-agnostic; comment prefix is decided per file type)
INJECTION_MARKER = "__HASH_INJECTED__:"
LOCK_MARKER = "__LOCKED__:"
INJECTION_RECORD_MARKER = "__INJECTION_RECORD__:"
REGISTRY_FILE = ".protection_registry.json"

# Core engine stays in Python while supporting marker injection/verification
# across these source-language extensions.
SUPPORTED_LANGUAGE_EXTENSIONS = {
    ".py",      # Python
    ".c",       # C
    ".h",       # C/C++ headers
    ".cpp",     # C++
    ".cc",      # C++
    ".cxx",     # C++
    ".hpp",     # C++ headers
    ".hh",      # C++ headers
    ".hxx",     # C++ headers
    ".java",    # Java
    ".cs",      # C#
    ".js",      # JavaScript
    ".php",     # PHP
}

def get_comment_prefix_for_file(file_path: str) -> str:
    """
    Return line-comment prefix for a supported source file.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".py":
        return "#"
    return "//"


def _format_marker_line(file_path: str, marker_token: str, value: str) -> str:
    """
    Build a marker line with the correct comment prefix for the target language.
    """
    prefix = get_comment_prefix_for_file(file_path)
    return f"{prefix} {marker_token} {value}".rstrip()


def _registry_path_for(file_path: str) -> str:
    """Registry is disabled; kept for compatibility with older helper flows."""
    return os.path.join(os.path.dirname(os.path.abspath(file_path)), REGISTRY_FILE)


def _load_registry(file_path: str) -> Dict[str, dict]:
    """Registry storage is disabled (in-file markers only)."""
    return {}


def _save_registry(file_path: str, registry: Dict[str, dict]) -> None:
    """Registry storage is disabled (in-file markers only)."""
    return None


def _registry_key(file_path: str) -> str:
    """Build a stable key for compatibility only."""
    return os.path.abspath(file_path)


def _get_registry_entry(file_path: str) -> Optional[dict]:
    """Registry is disabled; always returns None."""
    return None


def _mark_registry_injected(file_path: str, injection_hash: str) -> None:
    """Registry is disabled; no-op."""
    return None


def _mark_registry_tampered(file_path: str) -> None:
    """Registry is disabled; no-op."""
    return None


def _registry_was_injected(file_path: str) -> bool:
    """Registry is disabled; always False."""
    return False


def _registry_is_permanently_locked(file_path: str) -> bool:
    """Registry is disabled; always False."""
    return False


def check_injection_record(content: str) -> Tuple[bool, Optional[str]]:
    """
    Check if injection record exists in the code content.
    
    Args:
        content: File content as string
        
    Returns:
        Tuple of (record_exists, record_data)
        If record exists, returns (True, encoded_record_data)
        If not, returns (False, None)
    """
    lines = content.split('\n')
    
    for line in lines:
        stripped = line.strip()
        if INJECTION_RECORD_MARKER in stripped:
            # Extract record data from marker line
            record_data = stripped.split(INJECTION_RECORD_MARKER, 1)[1].strip()
            return True, record_data
    
    return False, None


def is_file_injected(file_path: str) -> bool:
    """
    Check if a file has injection record embedded in the code.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if injection record exists in file, False otherwise
    """
    if not os.path.exists(file_path):
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return False
    
    record_exists, _ = check_injection_record(content)
    return record_exists


def is_permanently_locked(file_path: str) -> bool:
    """
    Check if a file is permanently locked due to tampering.
    Checks the injection record in the code itself.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if permanently locked, False otherwise
    """
    if _registry_is_permanently_locked(file_path):
        return True
    
    if not os.path.exists(file_path):
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return False
    
    record_exists, record_data = check_injection_record(content)
    if not record_exists:
        return False
    
    # Decode and check if permanently locked
    try:
        decoded = base64.b64decode(record_data.encode('utf-8'))
        decompressed = gzip.decompress(decoded)
        record = json.loads(decompressed.decode('utf-8'))
        return record.get("permanently_locked", False)
    except Exception:
        return False


def create_injection_record(injection_hash: str, permanently_locked: bool = False) -> str:
    """
    Create an injection record to embed in the code.
    
    Args:
        injection_hash: The injection hash
        permanently_locked: Whether file is permanently locked
        
    Returns:
        Base64 encoded record string
    """
    record = {
        "injection_hash": injection_hash,
        "timestamp": time.time(),
        "locked": True,
        "permanently_locked": permanently_locked
    }
    
    record_json = json.dumps(record)
    compressed = gzip.compress(record_json.encode('utf-8'))
    encoded = base64.b64encode(compressed).decode('utf-8')
    return encoded


def embed_injection_record(file_path: str, injection_hash: str, permanently_locked: bool = False) -> bool:
    """
    Embed injection record directly into the code file.
    
    Args:
        file_path: Path to the file
        injection_hash: The injection hash
        permanently_locked: Whether to mark as permanently locked
        
    Returns:
        True if successful, False otherwise
    """
    if not os.path.exists(file_path):
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return False
    
    # Check if record already exists
    record_exists, existing_record = check_injection_record(content)
    
    if record_exists:
        # Update existing record if needed
        try:
            decoded = base64.b64decode(existing_record.encode('utf-8'))
            decompressed = gzip.decompress(decoded)
            record = json.loads(decompressed.decode('utf-8'))
            
            # Update if permanently locked
            if permanently_locked:
                record["permanently_locked"] = True
                record["tamper_timestamp"] = time.time()
                record["tampered"] = True
                
                # Re-encode and replace
                record_json = json.dumps(record)
                compressed = gzip.compress(record_json.encode('utf-8'))
                encoded = base64.b64encode(compressed).decode('utf-8')
                
                # Replace existing record line
                lines = content.split('\n')
                new_lines = []
                for line in lines:
                    if INJECTION_RECORD_MARKER in line.strip():
                        new_lines.append(_format_marker_line(file_path, INJECTION_RECORD_MARKER, encoded))
                    else:
                        new_lines.append(line)
                
                new_content = '\n'.join(new_lines)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True
        except Exception:
            pass
        return False
    
    # Create new record
    encoded_record = create_injection_record(injection_hash, permanently_locked)
    record_line = _format_marker_line(file_path, INJECTION_RECORD_MARKER, encoded_record)
    
    # Insert after hash injection marker
    lines = content.split('\n')
    new_lines = []
    record_inserted = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        # Insert record after injection marker
        if INJECTION_MARKER in line.strip() and not record_inserted:
            new_lines.append(record_line)
            record_inserted = True
    
    # If no injection marker found, insert at beginning
    if not record_inserted:
        if len(new_lines) > 0:
            new_lines.insert(1, record_line)
        else:
            new_lines.insert(0, record_line)
    
    new_content = '\n'.join(new_lines)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    except Exception:
        return False


def compute_file_hash(file_path: str) -> str:
    """
    Compute SHA-256 hash of a file.
    
    Args:
        file_path: Path to the file to hash
        
    Returns:
        Hexadecimal string representation of SHA-256 hash
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def check_hash_exists(content: str) -> Tuple[bool, str]:
    """
    Check if a hash has already been injected into the content.
    
    Args:
        content: File content as string
        
    Returns:
        Tuple of (hash_exists, existing_hash)
        If hash exists, returns (True, hash_value)
        If not, returns (False, "")
    """
    lines = content.split('\n')
    
    for line in lines:
        stripped = line.strip()
        if INJECTION_MARKER in stripped:
            # Extract hash from marker line
            hash_value = stripped.split(INJECTION_MARKER, 1)[1].strip()
            return True, hash_value
    
    return False, ""


def _python_runtime_guard_block() -> str:
    """
    Runtime self-verification block embedded in generated Python files.
    """
    return """# --- BEGIN ENGINE RUNTIME GUARD ---
import base64 as _ei_base64
import datetime as _ei_datetime
import gzip as _ei_gzip
import hashlib as _ei_hashlib
import os as _ei_os
import sys as _ei_sys

def _ei_block(_ei_reason: str, _ei_details: str = "") -> None:
    _ei_when = _ei_datetime.datetime.now().isoformat(timespec="seconds")
    print("=" * 60)
    print("EXECUTION BLOCKED")
    print("=" * 60)
    print(f"Reason: {_ei_reason}")
    print(f"Detected at: {_ei_when}")
    print(f"File: {_ei_os.path.abspath(__file__)}")
    if _ei_details:
        print("-" * 60)
        print(_ei_details)
    print("=" * 60)
    _ei_sys.exit(1)

def _ei_verify_self() -> None:
    # Build marker tokens dynamically so these literals do not look like marker lines.
    _ei_inj = "__HASH_INJECTED__" + ":"
    _ei_lock = "__LOCKED__" + ":"
    _ei_rec = "__INJECTION_RECORD__" + ":"
    try:
        with open(_ei_os.path.abspath(__file__), "r", encoding="utf-8") as _ei_f:
            _ei_content = _ei_f.read()
    except Exception as _ei_err:
        _ei_block("Could not read protected file", str(_ei_err))

    _ei_lines = _ei_content.split("\\n")
    _ei_stored_hash = None
    _ei_original_code = None

    for _ei_line in _ei_lines:
        _ei_stripped = _ei_line.strip()
        if _ei_inj in _ei_stripped:
            _ei_parts = _ei_stripped.split(_ei_inj, 1)[1].strip().split()
            if len(_ei_parts) >= 2:
                _ei_stored_hash = _ei_parts[1]
            elif len(_ei_parts) == 1:
                _ei_stored_hash = _ei_parts[0]
            if len(_ei_parts) >= 3:
                try:
                    _ei_encoded = _ei_parts[2]
                    _ei_compressed = _ei_base64.b64decode(_ei_encoded.encode("utf-8"))
                    _ei_original_code = _ei_gzip.decompress(_ei_compressed).decode("utf-8")
                except Exception:
                    _ei_original_code = None
            break

    if _ei_stored_hash is None:
        _ei_block(
            "Tampering detected: hash marker missing",
            "The __HASH_INJECTED__ marker line was not found. It may have been removed manually."
        )

    _ei_current_lines = []
    for _ei_line in _ei_lines:
        _ei_stripped = _ei_line.strip()
        if _ei_inj not in _ei_stripped and _ei_lock not in _ei_stripped and _ei_rec not in _ei_stripped:
            _ei_current_lines.append(_ei_line)
    _ei_current_code = "\\n".join(_ei_current_lines)
    _ei_current_hash = _ei_hashlib.sha256(_ei_current_code.encode("utf-8")).hexdigest()

    if _ei_current_hash != _ei_stored_hash:
        _ei_detail_lines = [
            "Integrity mismatch details:",
            f"Expected hash: {_ei_stored_hash}",
            f"Current hash:  {_ei_current_hash}",
        ]

        if _ei_original_code is not None:
            _ei_orig_lines = _ei_original_code.split("\\n")
            _ei_curr_lines = _ei_current_code.split("\\n")
            _ei_max = max(len(_ei_orig_lines), len(_ei_curr_lines))
            _ei_changes = []

            for _ei_idx in range(_ei_max):
                _ei_ln = _ei_idx + 1
                _ei_orig = _ei_orig_lines[_ei_idx] if _ei_idx < len(_ei_orig_lines) else None
                _ei_curr = _ei_curr_lines[_ei_idx] if _ei_idx < len(_ei_curr_lines) else None
                if _ei_orig != _ei_curr:
                    if _ei_orig is None:
                        _ei_changes.append(f"Line {_ei_ln}: ADDED -> {_ei_curr}")
                    elif _ei_curr is None:
                        _ei_changes.append(f"Line {_ei_ln}: REMOVED -> {_ei_orig}")
                    else:
                        _ei_changes.append(f"Line {_ei_ln}: CHANGED")
                        _ei_changes.append(f"  Original: {_ei_orig}")
                        _ei_changes.append(f"  Current:  {_ei_curr}")
                    if len(_ei_changes) >= 24:
                        _ei_changes.append("... more changes omitted ...")
                        break

            if _ei_changes:
                _ei_detail_lines.append("")
                _ei_detail_lines.append("Changed lines:")
                _ei_detail_lines.extend(_ei_changes)
        else:
            _ei_detail_lines.append("Original code payload unavailable; cannot compute line-by-line diff.")

        _ei_block("Tampering detected: code was modified", "\\n".join(_ei_detail_lines))

_ei_verify_self()
# --- END ENGINE RUNTIME GUARD ---"""


def _inject_python_runtime_guard(content: str) -> str:
    """
    Inject runtime guard in Python source before hash markers are added.
    """
    guard = _python_runtime_guard_block()
    if "# --- BEGIN ENGINE RUNTIME GUARD ---" in content:
        return content

    lines = content.split('\n')
    if lines and lines[0].startswith("#!"):
        # Keep shebang as first line.
        new_lines = [lines[0], guard]
        new_lines.extend(lines[1:])
        return '\n'.join(new_lines)

    return f"{guard}\n{content}"


def _javascript_runtime_guard_block() -> str:
    """
    Runtime self-verification block embedded in generated JavaScript files.
    """
    return """// --- BEGIN ENGINE RUNTIME GUARD ---
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

  const _ei_lines = _ei_content.split('\\n');
  let _ei_stored_hash = null;
  for (const _ei_line of _ei_lines) {
    const _ei_stripped = _ei_line.trim();
    if (_ei_stripped.includes(_ei_inj)) {
      const _ei_tail = _ei_stripped.split(_ei_inj, 2)[1].trim();
      const _ei_parts = _ei_tail.split(/\\s+/);
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
  const _ei_current_code = _ei_current_lines.join('\\n');
  const _ei_current_hash = _ei_sha256(_ei_current_code);

  if (_ei_current_hash !== _ei_stored_hash) {
    _ei_block(
      'Tampering detected: code was modified',
      `Expected hash: ${_ei_stored_hash}\\nCurrent hash:  ${_ei_current_hash}`
    );
  }

  globalThis.__EI_GUARD_OK__ = true;
}

_ei_verify_self();
// --- END ENGINE RUNTIME GUARD ---"""


def _javascript_runtime_tail_check_block() -> str:
    """
    Tail check to detect runtime-guard removal from the top of the file.
    """
    return """// --- BEGIN ENGINE RUNTIME TAIL CHECK ---
if (globalThis.__EI_GUARD_OK__ !== true) {
  console.log('============================================================');
  console.log('EXECUTION BLOCKED');
  console.log('============================================================');
  console.log('Reason: Tampering detected: runtime guard missing or removed');
  console.log('============================================================');
  process.exit(1);
}
// --- END ENGINE RUNTIME TAIL CHECK ---"""


def _inject_javascript_runtime_guard(content: str) -> str:
    """
    Inject runtime guard in JavaScript source before hash markers are added.
    """
    guard = _javascript_runtime_guard_block()
    tail_check = _javascript_runtime_tail_check_block()

    has_guard = "// --- BEGIN ENGINE RUNTIME GUARD ---" in content
    has_tail = "// --- BEGIN ENGINE RUNTIME TAIL CHECK ---" in content

    result = content
    if not has_guard:
        lines = result.split('\n')
        if lines and lines[0].startswith("#!"):
            # Keep shebang as first line.
            new_lines = [lines[0], guard]
            new_lines.extend(lines[1:])
            result = '\n'.join(new_lines)
        else:
            result = f"{guard}\n{result}"

    if not has_tail:
        result = f"{result}\n{tail_check}\n"

    return result


def _build_injected_content(file_path: str, content: str) -> Tuple[str, str, str, str]:
    """
    Build injected file content from full source content.

    Returns:
        Tuple of (new_content, injection_hash, code_hash, lock_hash)
    """
    # Compute hash of the original code content (this is used for verification)
    code_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

    # Store original code (compressed + encoded) for full detailed recovery/comparison
    original_code_bytes = content.encode('utf-8')
    compressed_code = gzip.compress(original_code_bytes)
    encoded_code = base64.b64encode(compressed_code).decode('utf-8')

    # Generate unique injection hash based on full source code + timestamp
    injection_data = f"{code_hash}:{time.time()}"
    injection_hash = hashlib.sha256(injection_data.encode('utf-8')).hexdigest()

    # Create lock hash
    lock_hash = hashlib.sha256(f"LOCK:{injection_hash}".encode('utf-8')).hexdigest()

    injection_line = _format_marker_line(
        file_path,
        INJECTION_MARKER,
        f"{injection_hash} {code_hash} {encoded_code}"
    )
    lock_line = _format_marker_line(file_path, LOCK_MARKER, lock_hash)

    lines = content.split('\n')
    if len(lines) == 0 or (len(lines) == 1 and lines[0].strip() == ''):
        new_content = f"{injection_line}\n{lock_line}\n"
    else:
        new_lines = [lines[0], injection_line, lock_line]
        new_lines.extend(lines[1:])
        new_content = '\n'.join(new_lines)

    return new_content, injection_hash, code_hash, lock_hash


def generate_injected_file(source_path: str, output_path: Optional[str] = None) -> Tuple[bool, str]:
    """
    Generate a new injected file from source without modifying the original.

    Args:
        source_path: Original source file path
        output_path: Optional output path. If None, uses <name>.customer<ext>

    Returns:
        Tuple of (success, message)
    """
    if not os.path.exists(source_path):
        return False, f"File not found: {source_path}"

    source_abs = os.path.abspath(source_path)
    source_dir = os.path.dirname(source_abs)
    source_name = os.path.basename(source_abs)
    source_root, source_ext = os.path.splitext(source_name)

    if output_path is None:
        output_abs = os.path.join(source_dir, f"{source_root}.customer{source_ext}")
    else:
        output_abs = os.path.abspath(output_path)

    if os.path.exists(output_abs):
        return False, f"Output file already exists: {output_abs}"

    try:
        with open(source_abs, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False, f"Error reading source file: {e}"

    hash_exists, _ = check_hash_exists(content)
    if hash_exists:
        return False, "Source file already contains injected hash markers. Use a clean file."

    # Embed startup self-verification code for supported runtimes.
    # This allows direct execution to block when code or markers are tampered with.
    if source_ext.lower() == ".py":
        content = _inject_python_runtime_guard(content)
    elif source_ext.lower() == ".js":
        content = _inject_javascript_runtime_guard(content)

    new_content, injection_hash, code_hash, lock_hash = _build_injected_content(source_abs, content)

    try:
        with open(output_abs, 'w', encoding='utf-8') as f:
            f.write(new_content)
    except Exception as e:
        return False, f"Error writing output file: {e}"

    # Embed record in the generated file so lock/tamper state travels with it.
    if not embed_injection_record(output_abs, injection_hash, permanently_locked=False):
        return False, f"Generated file but failed to embed injection record: {output_abs}"

    return True, (
        f"Generated customer file: {output_abs}\n"
        f"Code hash: {code_hash}\n"
        f"Injection hash: {injection_hash}\n"
        f"Lock hash: {lock_hash}"
    )


def generate_customer_folder(source_folder: str, output_folder: Optional[str] = None) -> Tuple[bool, Dict[str, str]]:
    """
    Generate a customer-ready protected copy of an entire folder.

    The folder is copied first, then each supported source file is replaced
    with an injected/protected version at the same path.

    Args:
        source_folder: Source project folder
        output_folder: Optional output folder path. If None, uses
            <source_folder>_customer

    Returns:
        Tuple of (overall_success, file_results)
    """
    source_abs = os.path.abspath(source_folder)
    if not os.path.isdir(source_abs):
        return False, {"<folder>": f"Folder not found: {source_folder}"}

    if output_folder is None:
        output_abs = f"{source_abs}_customer"
    else:
        output_abs = os.path.abspath(output_folder)

    if os.path.exists(output_abs):
        return False, {"<folder>": f"Output folder already exists: {output_abs}"}

    try:
        shutil.copytree(source_abs, output_abs)
    except Exception as e:
        return False, {"<folder>": f"Failed to copy folder: {e}"}

    source_files = iter_supported_files(output_abs, include_engine=True)
    if not source_files:
        return False, {"<folder>": "No supported source files found in folder"}

    overall_success = True
    results: Dict[str, str] = {
        "<folder>": f"Generated customer folder: {output_abs}"
    }

    for file_path in source_files:
        file_ext = os.path.splitext(file_path)[1]
        temp_output = f"{file_path}.customer_build{file_ext}"
        success, message = generate_injected_file(file_path, temp_output)
        relative_name = os.path.relpath(file_path, output_abs)

        if not success:
            results[relative_name] = f"FAILED: {message}"
            overall_success = False
            continue

        try:
            os.replace(temp_output, file_path)
            results[relative_name] = "Protected"
        except Exception as e:
            results[relative_name] = f"FAILED: unable to replace file: {e}"
            overall_success = False
            if os.path.exists(temp_output):
                try:
                    os.remove(temp_output)
                except Exception:
                    pass

    return overall_success, results


def inject_hash(file_path: str) -> bool:
    """
    Inject hash into the application file.
    
    Process:
    1. Check if permanently locked → block forever
    2. Check if hash already exists → block
    3. Check if registry says injection happened but hash missing → permanent lock
    4. If not injected → inject hash and record in registry
    
    Args:
        file_path: Path to the application file
        
    Returns:
        True if injection successful, False if already injected or error
    """
    abs_path = os.path.abspath(file_path)
    
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return False
    
    # Check if permanently locked
    if is_permanently_locked(file_path):
        print("=" * 60)
        print("PERMANENTLY LOCKED - TAMPERING DETECTED")
        print("=" * 60)
        print(f"\nFile: {file_path}")
        print("\nThis file has been permanently locked due to tampering.")
        print("The hash was manually deleted after injection.")
        print("\nExecution is permanently blocked.")
        print("=" * 60)
        return False
    
    # Read current file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Check if hash already exists in file
    hash_exists, existing_hash = check_hash_exists(content)
    
    # Check injection state: if injected before but hash is now missing → TAMPERING!
    injected_before = is_file_injected(file_path) or _registry_was_injected(file_path)
    if injected_before and not hash_exists:
        print("=" * 60)
        print("TAMPERING DETECTED - PERMANENT LOCK")
        print("=" * 60)
        print(f"\nFile: {file_path}")
        print("\nCRITICAL: Protected file no longer has hash marker!")
        print("This indicates manual tampering - hash was deleted.")
        print("\nThe file is now PERMANENTLY LOCKED.")
        print("Execution will be blocked forever.")
        print("=" * 60)
        
        # Mark as permanently tampered in the code itself
        embed_injection_record(file_path, "", permanently_locked=True)
        _mark_registry_tampered(file_path)
        return False
    
    # If hash exists, check if it matches registry
    if hash_exists:
        print(f"BLOCKED: Hash already injected!")
        print(f"Existing hash: {existing_hash}")
        print("System detected previous injection - blocking further attempts.")
        
        # Ensure injection record exists in code
        if not is_file_injected(file_path):
            injection_hash_part = existing_hash.split()[0] if existing_hash else ""
            embed_injection_record(file_path, injection_hash_part, permanently_locked=False)
        
        if existing_hash:
            _mark_registry_injected(file_path, existing_hash.split()[0])
        
        return False
    
    new_content, injection_hash, code_hash, lock_hash = _build_injected_content(file_path, content)
    
    # Write back to file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # Embed injection record directly in the code
        embed_injection_record(file_path, injection_hash, permanently_locked=False)
        _mark_registry_injected(file_path, injection_hash)
        
        print(f"SUCCESS: Hash injected into {file_path}")
        print(f"Code hash: {code_hash}")
        print(f"Injection hash: {injection_hash}")
        print(f"Lock hash: {lock_hash}")
        print("File is now locked - further injections are blocked.")
        print("Injection record embedded in code - tampering will be detected.")
        print("App will verify code integrity on startup.")
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False


def verify_injection(file_path: str) -> bool:
    """
    Verify that a hash injection exists and is valid.
    Also checks for tampering (registry says injected but hash missing).
    
    Args:
        file_path: Path to the application file
        
    Returns:
        True if valid injection exists, False otherwise
    """
    abs_path = os.path.abspath(file_path)
    
    if not os.path.exists(file_path):
        return False
    
    # Check if permanently locked
    if is_permanently_locked(file_path):
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return False
    
    hash_exists, hash_value = check_hash_exists(content)
    
    # Critical check: if historical injection exists but hash is missing → TAMPERING!
    if (is_file_injected(file_path) or _registry_was_injected(file_path)) and not hash_exists:
        # Mark as permanently tampered in the code itself
        embed_injection_record(file_path, "", permanently_locked=True)
        _mark_registry_tampered(file_path)
        return False
    
    if hash_exists and len(hash_value) > 0:
        _mark_registry_injected(file_path, hash_value.split()[0])
    
    return hash_exists and len(hash_value) > 0


def get_original_and_current_code(file_path: str) -> Tuple[bool, str, Optional[str], Optional[str]]:
    """
    Read both stored original code (from injection marker) and current code in file.

    Args:
        file_path: Path to protected source file

    Returns:
        Tuple of (success, message, original_code, current_code)
    """
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}", None, None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False, f"Error reading file: {e}", None, None

    lines = content.split('\n')
    original_code: Optional[str] = None

    for line in lines:
        stripped = line.strip()
        if INJECTION_MARKER not in stripped:
            continue

        # Expected format:
        # <comment> __HASH_INJECTED__: <injection_hash> <code_hash> <encoded_original_code>
        # Older formats may not include original code.
        parts = stripped.split(INJECTION_MARKER, 1)[1].strip().split()
        if len(parts) >= 3:
            try:
                encoded_code = parts[2]
                compressed_code = base64.b64decode(encoded_code.encode('utf-8'))
                original_code_bytes = gzip.decompress(compressed_code)
                original_code = original_code_bytes.decode('utf-8')
            except Exception:
                original_code = None
        break

    # Build current file code without protection marker lines.
    current_code_lines = []
    for line in lines:
        stripped = line.strip()
        if (
            INJECTION_MARKER not in stripped
            and LOCK_MARKER not in stripped
            and INJECTION_RECORD_MARKER not in stripped
        ):
            current_code_lines.append(line)
    current_code = '\n'.join(current_code_lines)

    if original_code is None:
        return (
            False,
            "Original code is not available in this injection format.",
            None,
            current_code
        )

    return True, "Original and current code loaded", original_code, current_code


def verify_code_integrity(file_path: str) -> Tuple[bool, str]:
    """
    Verify that the code hasn't been modified by comparing current hash with stored hash.
    Reports specific line numbers and code that changed.
    Also checks for permanent locks due to tampering.
    
    Args:
        file_path: Path to the application file
        
    Returns:
        Tuple of (is_valid, message)
        If code is valid: (True, "OK")
        If code was modified: (False, error_message with line details)
        If permanently locked: (False, "Permanently locked - tampering detected")
    """
    abs_path = os.path.abspath(file_path)
    
    if not os.path.exists(file_path):
        return False, "File not found"
    
    # Check if permanently locked
    if is_permanently_locked(file_path):
        return False, "PERMANENTLY LOCKED: Hash was manually deleted after injection. Tampering detected. Execution blocked forever."
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False, f"Error reading file: {e}"
    
    # Check if historical injection exists but hash is missing → TAMPERING!
    hash_exists, _ = check_hash_exists(content)
    if (is_file_injected(file_path) or _registry_was_injected(file_path)) and not hash_exists:
        embed_injection_record(file_path, "", permanently_locked=True)
        _mark_registry_tampered(file_path)
        return False, "TAMPERING DETECTED: Hash was manually deleted. File is now permanently locked."
    
    # Extract stored hash and original code from injection marker
    lines = content.split('\n')
    stored_code_hash = None
    original_code = None
    
    for i, line in enumerate(lines):
        if INJECTION_MARKER in line.strip():
            # Format: # __HASH_INJECTED__: <injection_hash> <code_hash> <encoded_original_code>
            # Or old format: # __HASH_INJECTED__: <hash>
            parts = line.split(INJECTION_MARKER, 1)[1].strip().split()
            if len(parts) >= 3:
                stored_code_hash = parts[1]  # Second part is the code hash
                # Decode and decompress original code
                try:
                    encoded_code = parts[2]
                    compressed_code = base64.b64decode(encoded_code.encode('utf-8'))
                    original_code_bytes = gzip.decompress(compressed_code)
                    original_code = original_code_bytes.decode('utf-8')
                except Exception:
                    original_code = None
            elif len(parts) >= 2:
                stored_code_hash = parts[1]
            elif len(parts) == 1:
                # Old format - use the hash as code hash
                stored_code_hash = parts[0]
            break
    
    if stored_code_hash is None:
        return False, "No hash found in file"
    
    # Remove hash marker lines and injection record to get current code
    current_code_lines = []
    for line in lines:
        stripped = line.strip()
        if (INJECTION_MARKER not in stripped and
            LOCK_MARKER not in stripped and
            INJECTION_RECORD_MARKER not in stripped):
            current_code_lines.append(line)
    
    # Compute hash of current code
    current_code_content = '\n'.join(current_code_lines)
    current_hash = hashlib.sha256(current_code_content.encode('utf-8')).hexdigest()
    
    # Compare hashes
    if current_hash == stored_code_hash:
        return True, "Code integrity verified"
    else:
        # Code was modified - find which lines changed
        error_msg = f"CODE MODIFIED! Hash mismatch: Expected {stored_code_hash[:16]}..., Got {current_hash[:16]}...\n\n"
        
        if original_code is not None:
            # Compare line by line
            original_lines = original_code.split('\n')
            current_lines = current_code_content.split('\n')
            
            changes = []
            max_lines = max(len(original_lines), len(current_lines))
            
            for line_num in range(max_lines):
                line_idx = line_num + 1  # 1-based line numbers
                orig_line = original_lines[line_num] if line_num < len(original_lines) else None
                curr_line = current_lines[line_num] if line_num < len(current_lines) else None
                
                if orig_line != curr_line:
                    if orig_line is None:
                        changes.append(f"Line {line_idx}: ADDED - '{curr_line}'")
                    elif curr_line is None:
                        changes.append(f"Line {line_idx}: REMOVED - '{orig_line}'")
                    else:
                        changes.append(f"Line {line_idx}: CHANGED")
                        changes.append(f"  Original: {orig_line}")
                        changes.append(f"  Current:  {curr_line}")
            
            if changes:
                error_msg += "DETAILED CHANGES:\n" + "=" * 60 + "\n"
                error_msg += "\n".join(changes)
            else:
                error_msg += "Unable to determine specific line changes."
        else:
            error_msg += "Unable to compare line-by-line (original code not stored)."
        
        return False, error_msg


# ============================================================================
# Hash Engine (SHA-256)
# ============================================================================

class HashEngine:
    """
    SHA-256 hash computation engine for code integrity verification.
    """
    
    @staticmethod
    def compute_file_hash(file_path: str) -> Optional[str]:
        """
        Compute SHA-256 hash of a file.
        
        Args:
            file_path: Path to the file to hash
            
        Returns:
            Hexadecimal string representation of SHA-256 hash, or None on error
        """
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except (IOError, OSError) as e:
            print(f"Error computing hash for {file_path}: {e}")
            return None
    
    @staticmethod
    def compute_string_hash(content: str) -> str:
        """
        Compute SHA-256 hash of a string.
        
        Args:
            content: String content to hash
            
        Returns:
            Hexadecimal string representation of SHA-256 hash
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()


# ============================================================================
# CRC Engine (CRC-32)
# ============================================================================

class CRCEngine:
    """
    CRC-32 checksum computation engine for code integrity verification.
    """
    
    @staticmethod
    def compute_file_crc(file_path: str) -> Optional[int]:
        """
        Compute CRC-32 checksum of a file.
        
        Args:
            file_path: Path to the file to checksum
            
        Returns:
            CRC-32 checksum as integer, or None on error
        """
        try:
            crc_value = 0
            with open(file_path, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    crc_value = zlib.crc32(byte_block, crc_value)
            return crc_value & 0xffffffff  # Ensure unsigned 32-bit
        except (IOError, OSError) as e:
            print(f"Error computing CRC for {file_path}: {e}")
            return None
    
    @staticmethod
    def compute_string_crc(content: str) -> int:
        """
        Compute CRC-32 checksum of a string.
        
        Args:
            content: String content to checksum
            
        Returns:
            CRC-32 checksum as integer
        """
        return zlib.crc32(content.encode('utf-8')) & 0xffffffff


# ============================================================================
# HMAC Engine (HMAC-SHA256)
# ============================================================================

class HMACEngine:
    """
    HMAC-SHA256 computation engine for code integrity verification.
    """
    
    KEY_FILE = '.integrity_key'
    
    @classmethod
    def _get_key_file_path(cls) -> str:
        """
        Get the absolute path to the HMAC key file.
        
        Returns:
            Absolute path to the key file
        """
        # Get current directory (where engine.py is located)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, cls.KEY_FILE)
    
    @classmethod
    def get_or_create_key(cls) -> bytes:
        """
        Get existing HMAC key or create a new one if it doesn't exist.
        
        Returns:
            HMAC secret key as bytes
        """
        key_path = cls._get_key_file_path()
        
        if os.path.exists(key_path):
            with open(key_path, 'rb') as f:
                return f.read()
        else:
            key = secrets.token_bytes(32)
            with open(key_path, 'wb') as f:
                f.write(key)
            return key
    
    @classmethod
    def compute_file_hmac(cls, file_path: str) -> Optional[str]:
        """
        Compute HMAC-SHA256 of a file.
        
        Args:
            file_path: Path to the file to compute HMAC for
            
        Returns:
            Hexadecimal string representation of HMAC-SHA256, or None on error
        """
        try:
            key = cls.get_or_create_key()
            hmac_hash = hmac.new(key, digestmod=hashlib.sha256)
            
            with open(file_path, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    hmac_hash.update(byte_block)
            
            return hmac_hash.hexdigest()
        except (IOError, OSError) as e:
            print(f"Error computing HMAC for {file_path}: {e}")
            return None
    
    @classmethod
    def compute_string_hmac(cls, content: str) -> str:
        """
        Compute HMAC-SHA256 of a string.
        
        Args:
            content: String content to compute HMAC for
            
        Returns:
            Hexadecimal string representation of HMAC-SHA256
        """
        key = cls.get_or_create_key()
        return hmac.new(key, content.encode('utf-8'), hashlib.sha256).hexdigest()


# ============================================================================
# Manifest Management
# ============================================================================

class Manifest:
    """
    Manifest handler for integrity verification system.
    """
    
    MANIFEST_FILENAME = 'manifest.json'
    
    def __init__(self, manifest_path: Optional[str] = None):
        """
        Initialize manifest handler.
        
        Args:
            manifest_path: Path to manifest file. If None, uses default.
        """
        if manifest_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            manifest_path = os.path.join(current_dir, self.MANIFEST_FILENAME)
        
        self.manifest_path = manifest_path
        self.data: Dict = {"files": {}, "version": "1.0"}
    
    def add_file_entry(self, relative_path: str, sha256: str, crc: int, hmac: str):
        """
        Add or update a file entry in the manifest.
        
        Args:
            relative_path: Relative path to the file
            sha256: SHA-256 hash value
            crc: CRC-32 checksum value
            hmac: HMAC-SHA256 value
        """
        normalized_path = relative_path.replace('\\', '/')
        
        self.data["files"][normalized_path] = {
            "sha256": sha256,
            "crc": crc,
            "hmac": hmac
        }
    
    def get_file_entry(self, relative_path: str) -> Optional[Dict]:
        """
        Get integrity values for a file from the manifest.
        
        Args:
            relative_path: Relative path to the file
            
        Returns:
            Dictionary with sha256, crc, and hmac keys, or None if not found
        """
        normalized_path = relative_path.replace('\\', '/')
        return self.data["files"].get(normalized_path)
    
    def save(self) -> bool:
        """
        Save manifest to disk.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.manifest_path, 'w') as f:
                json.dump(self.data, f, indent=2)
            return True
        except (IOError, OSError) as e:
            print(f"Error saving manifest: {e}")
            return False
    
    def load(self) -> bool:
        """
        Load manifest from disk.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(self.manifest_path):
                return False
            
            with open(self.manifest_path, 'r') as f:
                self.data = json.load(f)
            return True
        except (IOError, OSError, json.JSONDecodeError) as e:
            print(f"Error loading manifest: {e}")
            return False
    
    def get_all_files(self) -> Dict:
        """
        Get all file entries from the manifest.
        
        Returns:
            Dictionary mapping file paths to their integrity values
        """
        return self.data.get("files", {})


# ============================================================================
# Verifier
# ============================================================================

class Verifier:
    """
    Integrity verifier that compares runtime values against manifest.
    """
    
    def __init__(self, manifest: Manifest, base_path: str):
        """
        Initialize verifier.
        
        Args:
            manifest: Manifest instance containing trusted values
            base_path: Base path for resolving relative file paths
        """
        self.manifest = manifest
        self.base_path = os.path.abspath(base_path)
    
    def verify_file(self, relative_path: str) -> Tuple[bool, Dict[str, bool]]:
        """
        Verify integrity of a single file.
        
        Args:
            relative_path: Relative path to the file (from base_path)
            
        Returns:
            Tuple of (overall_verification_passed, individual_checks)
            where individual_checks is a dict with keys: sha256, crc, hmac
        """
        trusted = self.manifest.get_file_entry(relative_path)
        if trusted is None:
            return False, {"sha256": False, "crc": False, "hmac": False}
        
        file_path = os.path.join(self.base_path, relative_path)
        if not os.path.exists(file_path):
            return False, {"sha256": False, "crc": False, "hmac": False}
        
        current_sha256 = HashEngine.compute_file_hash(file_path)
        current_crc = CRCEngine.compute_file_crc(file_path)
        current_hmac = HMACEngine.compute_file_hmac(file_path)
        
        sha256_match = current_sha256 is not None and current_sha256 == trusted["sha256"]
        crc_match = current_crc is not None and current_crc == trusted["crc"]
        hmac_match = current_hmac is not None and current_hmac == trusted["hmac"]
        
        overall_match = sha256_match and crc_match and hmac_match
        
        return overall_match, {
            "sha256": sha256_match,
            "crc": crc_match,
            "hmac": hmac_match
        }
    
    def verify_all(self) -> Dict[str, Tuple[bool, Dict[str, bool]]]:
        """
        Verify integrity of all files in the manifest.
        
        Returns:
            Dictionary mapping file paths to (overall_match, individual_checks)
        """
        results = {}
        all_files = self.manifest.get_all_files()
        
        for relative_path in all_files.keys():
            results[relative_path] = self.verify_file(relative_path)
        
        return results


# ============================================================================
# Scorer
# ============================================================================

class Scorer:
    """
    Integrity scoring engine that computes composite scores.
    """
    
    BASE_SCORE = 100
    SHA256_PENALTY = 50
    CRC_PENALTY = 20
    HMAC_PENALTY = 20
    DECOY_PENALTY = 100
    EXECUTION_THRESHOLD = 80
    
    @classmethod
    def compute_score(cls, verification_results: Dict[str, Tuple[bool, Dict[str, bool]]], 
                     decoy_triggered: bool = False) -> int:
        """
        Compute composite integrity score from verification results.
        
        Args:
            verification_results: Dictionary mapping file paths to
                (overall_match, individual_checks) tuples
            decoy_triggered: Whether decoy memory trap was triggered
            
        Returns:
            Composite integrity score (0-100)
        """
        score = cls.BASE_SCORE
        
        for relative_path, (overall_match, checks) in verification_results.items():
            if not checks["sha256"]:
                score -= cls.SHA256_PENALTY
            if not checks["crc"]:
                score -= cls.CRC_PENALTY
            if not checks["hmac"]:
                score -= cls.HMAC_PENALTY
        
        if decoy_triggered:
            score -= cls.DECOY_PENALTY
        
        return max(0, score)
    
    @classmethod
    def can_execute(cls, score: int) -> bool:
        """
        Determine if execution is allowed based on score.
        
        Args:
            score: Composite integrity score
            
        Returns:
            True if score >= threshold, False otherwise
        """
        return score >= cls.EXECUTION_THRESHOLD
    
    @classmethod
    def get_threshold(cls) -> int:
        """
        Get the execution threshold value.
        
        Returns:
            Execution threshold score
        """
        return cls.EXECUTION_THRESHOLD


# ============================================================================
# Runtime Monitor
# ============================================================================

class RuntimeMonitor:
    """
    Background thread that continuously monitors code integrity.
    """
    
    def __init__(self, verifier: Verifier, check_interval: float = 2.0,
                 on_tamper_detected: Optional[Callable[[], None]] = None):
        """
        Initialize runtime monitor.
        
        Args:
            verifier: Verifier instance to use for integrity checks
            check_interval: Time in seconds between integrity checks
            on_tamper_detected: Callback function called when tampering is detected
        """
        self.verifier = verifier
        self.check_interval = check_interval
        self.on_tamper_detected = on_tamper_detected
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
    
    def _monitor_loop(self):
        """Main monitoring loop that runs in background thread."""
        while self._running:
            try:
                results = self.verifier.verify_all()
                
                for relative_path, (overall_match, checks) in results.items():
                    if not overall_match:
                        if self.on_tamper_detected:
                            self.on_tamper_detected()
                        return
                
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"Runtime monitor error: {e}")
                if self.on_tamper_detected:
                    self.on_tamper_detected()
                return
    
    def start(self):
        """Start the runtime monitoring thread."""
        with self._lock:
            if self._running:
                return
            
            self._running = True
            self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._thread.start()
    
    def stop(self):
        """Stop the runtime monitoring thread."""
        with self._lock:
            self._running = False
            if self._thread:
                self._thread.join(timeout=1.0)


# ============================================================================
# Decoy Memory
# ============================================================================

class DecoyMemory:
    """
    Decoy memory trap for detecting runtime tampering.
    """
    
    def __init__(self, on_triggered: Optional[Callable[[], None]] = None):
        """
        Initialize decoy memory trap.
        
        Args:
            on_triggered: Callback function called when decoy is triggered
        """
        self.on_triggered = on_triggered
        self._decoy_data = self._create_decoy_data()
        self._monitoring = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._triggered = False
    
    def _create_decoy_data(self) -> dict:
        """
        Create decoy data structures that should never be accessed.
        
        Returns:
            Dictionary containing fake data structures
        """
        return {
            'decoy_var_1': random.randint(1000000, 9999999),
            'decoy_var_2': ''.join(chr(random.randint(65, 90)) for _ in range(20)),
            'decoy_var_3': [random.random() for _ in range(10)],
            'decoy_var_4': {'key': random.randint(0, 1000)},
            'decoy_secret': bytes([random.randint(0, 255) for _ in range(32)])
        }
    
    def _monitor_loop(self):
        """Monitor decoy memory for unexpected access."""
        initial_state = self._get_decoy_state()
        
        while self._monitoring:
            try:
                current_state = self._get_decoy_state()
                
                if current_state != initial_state:
                    self._triggered = True
                    if self.on_triggered:
                        self.on_triggered()
                    return
                
                time.sleep(0.1)
            except Exception:
                self._triggered = True
                if self.on_triggered:
                    self.on_triggered()
                return
    
    def _get_decoy_state(self) -> tuple:
        """
        Get current state of decoy data for comparison.
        
        Returns:
            Tuple representing current state
        """
        return (
            self._decoy_data['decoy_var_1'],
            self._decoy_data['decoy_var_2'],
            len(self._decoy_data['decoy_var_3']),
            self._decoy_data['decoy_var_4'].get('key'),
            len(self._decoy_data['decoy_secret'])
        )
    
    def start(self):
        """Start monitoring decoy memory."""
        with self._lock:
            if self._monitoring:
                return
            
            self._monitoring = True
            self._triggered = False
            self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._thread.start()
    
    def stop(self):
        """Stop monitoring decoy memory."""
        with self._lock:
            self._monitoring = False
            if self._thread:
                self._thread.join(timeout=0.5)
    
    def is_triggered(self) -> bool:
        """
        Check if decoy trap has been triggered.
        
        Returns:
            True if decoy was triggered, False otherwise
        """
        return self._triggered
    
    def get_decoy_data(self) -> dict:
        """
        Get decoy data (for testing purposes).
        
        Returns:
            Dictionary containing decoy data
        """
        return self._decoy_data


# ============================================================================
# Main Entry Point
# ============================================================================

def auto_protect_file(file_path: str) -> Tuple[bool, str]:
    """
    Automatically protect a file: inject hash if not present, verify if present.
    Detects tampering if hash was manually deleted.
    
    Args:
        file_path: Path to the Python file to protect
        
    Returns:
        Tuple of (success, message)
        If hash injected: (True, "Hash injected")
        If hash verified: (True, "Hash verified")
        If verification failed: (False, error_message)
        If permanently locked: (False, "Permanently locked - tampering detected")
    """
    abs_path = os.path.abspath(file_path)
    
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"
    
    # Check if permanently locked
    if is_permanently_locked(file_path):
        return False, "PERMANENTLY LOCKED: Hash was manually deleted after injection. Tampering detected. Execution blocked forever."
    
    # Registry-backed tamper check: injected before but hash marker removed.
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            current_content = f.read()
        has_hash_marker, _ = check_hash_exists(current_content)
        if _registry_was_injected(file_path) and not has_hash_marker:
            embed_injection_record(file_path, "", permanently_locked=True)
            _mark_registry_tampered(file_path)
            return False, "TAMPERING DETECTED: Hash marker was manually removed. File is permanently locked."
    except Exception as e:
        return False, f"Error reading file: {e}"
    
    # Check if hash already exists
    if verify_injection(file_path):
        # Hash exists - verify integrity
        is_valid, message = verify_code_integrity(file_path)
        if is_valid:
            return True, "Code integrity verified"
        else:
            return False, message
    else:
        # Check if injection record/registry exists but hash is missing → TAMPERING!
        if is_file_injected(file_path) or _registry_was_injected(file_path):
            # Hash was deleted manually - permanent lock in code
            embed_injection_record(file_path, "", permanently_locked=True)
            _mark_registry_tampered(file_path)
            return False, "TAMPERING DETECTED: Hash was manually deleted. File is now permanently locked."
        
        # No hash and no injection record - safe to inject
        success = inject_hash(file_path)
        if success:
            return True, "Hash automatically injected"
        else:
            return False, "Failed to inject hash"


def run_protected_file(file_path: str):
    """
    Run a Python file with automatic protection:
    - Auto-inject hash if not present
    - Verify hash if present
    - Block execution if code is modified
    
    Args:
        file_path: Path to the Python file to run
    """
    # Auto-protect the file
    success, message = auto_protect_file(file_path)
    
    if not success:
        print("=" * 60)
        print("CODE PROTECTION FAILED")
        print("=" * 60)
        print(f"ERROR: {message}")
        print("\nExecution blocked for security reasons.")
        print("=" * 60)
        sys.exit(1)
    
    # If hash was just injected, show message
    if "injected" in message.lower():
        print(f"[AUTO-PROTECT] Hash injected into {file_path}")
    
    # Run the file
    try:
        import subprocess
        result = subprocess.run([sys.executable, file_path], check=False)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Error running file: {e}")
        sys.exit(1)


def iter_supported_files(folder_path: str, include_engine: bool = False) -> List[str]:
    """
    Collect supported source files from a folder recursively.
    
    Args:
        folder_path: Root folder to scan
        include_engine: Whether to include this engine file itself
        
    Returns:
        Sorted list of absolute supported file paths
    """
    excluded_dirs = {
        "__pycache__",
        ".git",
        ".venv",
        "venv",
        "env",
        "node_modules"
    }
    
    folder_abs = os.path.abspath(folder_path)
    engine_abs = os.path.abspath(__file__)
    found_files: List[str] = []
    
    for root, dirs, files in os.walk(folder_abs):
        dirs[:] = [d for d in dirs if d not in excluded_dirs and not d.startswith('.')]
        
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext not in SUPPORTED_LANGUAGE_EXTENSIONS:
                continue
            
            full_path = os.path.abspath(os.path.join(root, filename))
            
            # Avoid self-locking the protection engine unless explicitly requested.
            if not include_engine and full_path == engine_abs:
                continue
            
            found_files.append(full_path)
    
    return sorted(found_files)


def auto_protect_folder(folder_path: str, include_engine: bool = False) -> Tuple[bool, Dict[str, str]]:
    """
    Automatically protect all supported source files in a folder.
    
    Args:
        folder_path: Root folder containing supported source files
        include_engine: Whether to include this engine file itself
        
    Returns:
        Tuple of:
            - overall_success (True when all files are protected/verified)
            - file_results (relative_path -> result message)
    """
    folder_abs = os.path.abspath(folder_path)
    
    if not os.path.isdir(folder_abs):
        return False, {"<folder>": f"Folder not found: {folder_path}"}
    
    source_files = iter_supported_files(folder_abs, include_engine=include_engine)
    if not source_files:
        return False, {"<folder>": "No supported source files found in folder"}
    
    overall_success = True
    results: Dict[str, str] = {}
    
    for file_path in source_files:
        success, message = auto_protect_file(file_path)
        relative_name = os.path.relpath(file_path, folder_abs)
        results[relative_name] = message
        
        if not success:
            overall_success = False
    
    return overall_success, results


def verify_folder_integrity(folder_path: str, include_engine: bool = False) -> Tuple[bool, Dict[str, str]]:
    """
    Verify integrity for all supported source files in a folder.
    
    Args:
        folder_path: Root folder containing supported source files
        include_engine: Whether to include this engine file itself
        
    Returns:
        Tuple of:
            - overall_success (True only if all files pass verification)
            - file_results (relative_path -> verification message)
    """
    folder_abs = os.path.abspath(folder_path)
    
    if not os.path.isdir(folder_abs):
        return False, {"<folder>": f"Folder not found: {folder_path}"}
    
    source_files = iter_supported_files(folder_abs, include_engine=include_engine)
    if not source_files:
        return False, {"<folder>": "No supported source files found in folder"}
    
    overall_success = True
    results: Dict[str, str] = {}
    
    for file_path in source_files:
        success, message = verify_code_integrity(file_path)
        relative_name = os.path.relpath(file_path, folder_abs)
        results[relative_name] = message
        
        if not success:
            overall_success = False
    
    return overall_success, results


def strip_protection_markers(file_path: str) -> Tuple[bool, str]:
    """
    Remove all injected protection marker lines from a file.
    Intended for development reset flows.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False, f"Error reading file: {e}"
    
    original_lines = content.split('\n')
    cleaned_lines = []
    removed = 0
    for line in original_lines:
        stripped = line.strip()
        if (
            INJECTION_MARKER in stripped
            or LOCK_MARKER in stripped
            or INJECTION_RECORD_MARKER in stripped
        ):
            removed += 1
            continue
        cleaned_lines.append(line)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(cleaned_lines))
        return True, f"Removed {removed} marker line(s)"
    except Exception as e:
        return False, f"Error writing file: {e}"


def dev_reset_folder(folder_path: str, include_engine: bool = False) -> Tuple[bool, Dict[str, str]]:
    """
    Development reset:
    - remove protection markers from all supported source files
    - delete local protection registry
    """
    folder_abs = os.path.abspath(folder_path)
    if not os.path.isdir(folder_abs):
        return False, {"<folder>": f"Folder not found: {folder_path}"}
    
    results: Dict[str, str] = {}
    success_all = True
    
    source_files = iter_supported_files(folder_abs, include_engine=include_engine)
    for file_path in source_files:
        ok, msg = strip_protection_markers(file_path)
        rel = os.path.relpath(file_path, folder_abs)
        results[rel] = msg
        if not ok:
            success_all = False
    
    registry_path = os.path.join(folder_abs, REGISTRY_FILE)
    if os.path.exists(registry_path):
        try:
            os.remove(registry_path)
            results[REGISTRY_FILE] = "Deleted registry"
        except Exception as e:
            results[REGISTRY_FILE] = f"Failed to delete registry: {e}"
            success_all = False
    else:
        results[REGISTRY_FILE] = "Registry not found"
    
    return success_all, results


def main():
    """
    Main entry point for the engine.
    
    Usage:
        python engine.py <file>               # Inject hash only
        python engine.py <file.py> --run      # Auto-protect and run (Python only)
        python engine.py <file> --auto        # Auto-protect (inject if needed, verify if exists)
        python engine.py <file> --generate    # Create new customer copy (self-protected)
        python engine.py <file> --generate <output_file>
        python engine.py <file> --show-codes  # Print original + current (customer) code
        python engine.py <folder> --generate-folder
        python engine.py <folder> --generate-folder <output_folder>
        python engine.py <folder> --auto      # Auto-protect supported files recursively
        python engine.py <folder> --verify    # Verify all injected supported files in folder
        python engine.py <folder> --dev-reset # Dev only: clear lock + remove markers
    """
    if len(sys.argv) < 2:
        print("=" * 60)
        print("Hash Injection Engine - Auto-Protect System")
        print("=" * 60)
        print("\nUsage:")
        print("  python engine.py <file>               # Inject hash only")
        print("  python engine.py <file.py> --run      # Auto-protect and run (Python only)")
        print("  python engine.py <file> --auto        # Auto-protect (inject/verify)")
        print("  python engine.py <file> --generate    # Generate new customer file")
        print("  python engine.py <file> --generate <out_file>")
        print("  python engine.py <file> --show-codes  # Print original/current code")
        print("  python engine.py <folder> --generate-folder")
        print("  python engine.py <folder> --generate-folder <out_folder>")
        print("  python engine.py <folder> --auto      # Auto-protect supported files")
        print("  python engine.py <folder> --verify    # Verify supported files")
        print("  python engine.py <folder> --dev-reset # Clear lock and markers")
        print("\nSupported file extensions:")
        print("  .py, .c, .h, .cpp, .cc, .cxx, .hpp, .hh, .hxx, .java, .cs, .js, .php")
        print("\nExamples:")
        print("  python engine.py app.py")
        print("  python engine.py app.py --run")
        print("  python engine.py app.py --auto")
        print("  python engine.py app.py --generate")
        print("  python engine.py app.py --generate app.customer.py")
        print("  python engine.py app.py --show-codes")
        print("  python engine.py ./my_project --generate-folder")
        print("  python engine.py ./my_project --generate-folder ./my_project_customer")
        print("  python engine.py ./my_project --auto")
        print("  python engine.py ./my_project --verify")
        print("  python engine.py ./my_project --dev-reset")
        sys.exit(1)
    
    target_path = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else None
    mode_arg = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Validate target
    if not os.path.exists(target_path):
        print(f"Error: Path not found: {target_path}")
        sys.exit(1)
    
    is_folder = os.path.isdir(target_path)
    app_file = target_path
    
    if is_folder:
        if mode is None:
            mode = "--auto"
        
        if mode not in ("--auto", "--verify", "--dev-reset", "--generate-folder"):
            print(f"Error: Mode {mode} is not supported for folders")
            print("Supported folder modes: --generate-folder, --auto, --verify, --dev-reset")
            sys.exit(1)
        
        print("=" * 60)
        print("FOLDER PROTECTION")
        print("=" * 60)
        print(f"\nFolder: {os.path.abspath(target_path)}")
        
        if mode == "--auto":
            success, file_results = auto_protect_folder(target_path)
            print("\nFile results:")
            for relative_name, message in file_results.items():
                marker = "✓" if "verified" in message.lower() or "injected" in message.lower() else "✗"
                print(f"  {marker} {relative_name}: {message}")
            
            print("\n" + "=" * 60)
            if success:
                print("FOLDER AUTO-PROTECT SUCCESSFUL")
                print("=" * 60)
                sys.exit(0)
            else:
                print("FOLDER AUTO-PROTECT FAILED")
                print("=" * 60)
                sys.exit(1)

        if mode == "--generate-folder":
            success, file_results = generate_customer_folder(target_path, mode_arg)
            print("\nGeneration results:")
            for relative_name, message in file_results.items():
                marker = "✓" if "failed" not in message.lower() else "✗"
                print(f"  {marker} {relative_name}: {message}")

            print("\n" + "=" * 60)
            if success:
                print("CUSTOMER FOLDER GENERATION SUCCESSFUL")
                print("=" * 60)
                sys.exit(0)
            else:
                print("CUSTOMER FOLDER GENERATION FAILED")
                print("=" * 60)
                sys.exit(1)
        
        if mode == "--dev-reset":
            success, file_results = dev_reset_folder(target_path)
            print("\nDev reset results:")
            for relative_name, message in file_results.items():
                marker = "✓" if "error" not in message.lower() and "failed" not in message.lower() else "✗"
                print(f"  {marker} {relative_name}: {message}")
            
            print("\n" + "=" * 60)
            if success:
                print("FOLDER DEV RESET COMPLETE")
                print("=" * 60)
                sys.exit(0)
            else:
                print("FOLDER DEV RESET FAILED")
                print("=" * 60)
                sys.exit(1)
        
        success, file_results = verify_folder_integrity(target_path)
        print("\nVerification results:")
        for relative_name, message in file_results.items():
            marker = "✓" if "verified" in message.lower() else "✗"
            print(f"  {marker} {relative_name}: {message}")
        
        print("\n" + "=" * 60)
        if success:
            print("FOLDER INTEGRITY VERIFIED")
            print("=" * 60)
            sys.exit(0)
        else:
            print("FOLDER INTEGRITY CHECK FAILED")
            print("=" * 60)
            sys.exit(1)
    
    app_ext = os.path.splitext(app_file)[1].lower()
    if app_ext not in SUPPORTED_LANGUAGE_EXTENSIONS:
        print(f"Error: {app_file} is not a supported source file")
        print("Supported extensions: " + ", ".join(sorted(SUPPORTED_LANGUAGE_EXTENSIONS)))
        sys.exit(1)
    
    # Mode: --show-codes
    if mode == "--show-codes":
        print("=" * 60)
        print("STORED ORIGINAL VS CURRENT CODE")
        print("=" * 60)
        print(f"\nFile: {app_file}")

        ok, msg, original_code, current_code = get_original_and_current_code(app_file)
        if not ok:
            print(f"\n✗ {msg}")
            if current_code is not None:
                print("\nCURRENT (CUSTOMER) CODE:")
                print("-" * 60)
                print(current_code)
            print("\n" + "=" * 60)
            print("SHOW CODES FAILED")
            print("=" * 60)
            sys.exit(1)

        print("\nORIGINAL CODE (stored at inject time):")
        print("-" * 60)
        print(original_code if original_code is not None else "")
        print("\nCURRENT (CUSTOMER) CODE:")
        print("-" * 60)
        print(current_code if current_code is not None else "")

        print("\n" + "=" * 60)
        print("SHOW CODES SUCCESSFUL")
        print("=" * 60)
        sys.exit(0)

    # Mode: --generate (create a new injected file)
    elif mode == "--generate":
        print("=" * 60)
        print("GENERATE INJECTED FILE")
        print("=" * 60)
        print(f"\nSource file: {app_file}")

        success, message = generate_injected_file(app_file, mode_arg)
        if not success:
            print(f"\n✗ {message}")
            print("\n" + "=" * 60)
            print("GENERATION FAILED")
            print("=" * 60)
            sys.exit(1)

        print(f"\n✓ {message}")
        print("\n" + "=" * 60)
        print("GENERATION SUCCESSFUL")
        print("=" * 60)
        sys.exit(0)

    # Mode: --run (auto-protect and run)
    elif mode == "--run":
        if app_ext != ".py":
            print("Error: --run mode is supported only for Python files")
            sys.exit(1)
        print("=" * 60)
        print("AUTO-PROTECT RUNNER")
        print("=" * 60)
        print(f"\nFile: {app_file}")
        
        # Auto-protect: inject hash if not present, verify if present
        print("\n[1/2] Checking protection status...")
        success, message = auto_protect_file(app_file)
        
        if not success:
            print(f"  ✗ {message}")
            print("\n" + "=" * 60)
            print("EXECUTION BLOCKED")
            print("=" * 60)
            print("\nThe code has been modified or protection failed!")
            print("Execution blocked for security reasons.")
            print("=" * 60)
            sys.exit(1)
        
        print(f"  ✓ {message}")
        
        # Final verification before running
        print("\n[2/2] Final integrity check...")
        is_valid, verify_msg = verify_code_integrity(app_file)
        
        if not is_valid:
            print(f"  ✗ {verify_msg}")
            print("\n" + "=" * 60)
            print("EXECUTION BLOCKED")
            print("=" * 60)
            print("\nCode integrity verification failed!")
            print("Execution blocked for security reasons.")
            print("=" * 60)
            sys.exit(1)
        
        print("  ✓ Code integrity verified")
        
        # Run the script
        print("\n" + "=" * 60)
        print("RUNNING PROTECTED SCRIPT")
        print("=" * 60 + "\n")
        
        try:
            import subprocess
            result = subprocess.run([sys.executable, app_file], check=False)
            sys.exit(result.returncode)
        except KeyboardInterrupt:
            print("\n\nExecution interrupted by user")
            sys.exit(130)
        except Exception as e:
            print(f"\nError running script: {e}")
            sys.exit(1)
    
    # Mode: --auto (auto-protect only, don't run)
    elif mode == "--auto":
        print("=" * 60)
        print("AUTO-PROTECT")
        print("=" * 60)
        print(f"\nFile: {app_file}")
        
        success, message = auto_protect_file(app_file)
        
        if not success:
            print(f"\n✗ {message}")
            print("\n" + "=" * 60)
            print("PROTECTION FAILED")
            print("=" * 60)
            sys.exit(1)
        
        print(f"\n✓ {message}")
        print("\n" + "=" * 60)
        print("PROTECTION SUCCESSFUL")
        print("=" * 60)
        sys.exit(0)
    
    # Mode: default (manual hash injection)
    else:
        print("=" * 60)
        print("Hash Injection Engine")
        print("=" * 60)
        print(f"\nTarget file: {app_file}")
        print("\n[1/2] Checking for existing hash injection...")
        
        # Check if hash already exists
        if verify_injection(app_file):
            print("  ✓ Hash injection detected")
            print("\n[2/2] Injection status: BLOCKED")
            print("\n" + "=" * 60)
            print("RESULT: Hash already exists - injection blocked!")
            print("=" * 60)
            sys.exit(0)
        
        print("  ✓ No existing hash found")
        print("\n[2/2] Injecting hash and locking file...")
        
        # Attempt injection
        success = inject_hash(app_file)
        
        print("\n" + "=" * 60)
        if success:
            print("RESULT: Hash successfully injected and locked!")
        else:
            print("RESULT: Injection failed or already exists!")
        print("=" * 60)
        
        sys.exit(0 if success else 1)


# ============================================================================
# Universal Protection Function
# ============================================================================

def protect_this_folder(folder_path: Optional[str] = None):
    """
    Protect every Python file in a folder.
    
    Args:
        folder_path: Folder path. If None, uses the caller file's directory.
    """
    import inspect
    
    if folder_path is None:
        frame = inspect.currentframe().f_back
        caller_file = frame.f_globals.get('__file__')
        
        if caller_file is None:
            print("Error: Could not determine calling file")
            sys.exit(1)
        
        folder_path = os.path.dirname(os.path.abspath(caller_file))
    
    success, results = auto_protect_folder(folder_path)
    
    if not success:
        print("=" * 60)
        print("FOLDER PROTECTION FAILED")
        print("=" * 60)
        for relative_name, message in results.items():
            print(f"✗ {relative_name}: {message}")
        print("=" * 60)
        sys.exit(1)


def protect_this_file():
    """
    Universal protection function - call this at the top of ANY Python file.
    
    Usage in your app:
        from engine import protect_this_file
        protect_this_file()
    
    Or:
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from engine import protect_this_file
        protect_this_file()
    
    This function will:
    - Auto-inject hash on first run if not present
    - Verify code integrity on subsequent runs
    - Block execution if code is modified
    - Permanently lock if hash is manually deleted
    """
    import sys
    import os
    
    # Get the file that called this function
    import inspect
    frame = inspect.currentframe().f_back
    caller_file = frame.f_globals.get('__file__')
    
    if caller_file is None:
        print("Error: Could not determine calling file")
        sys.exit(1)
    
    file_path = os.path.abspath(caller_file)
    
    # Auto-protect: inject hash if not present, verify if present
    success, message = auto_protect_file(file_path)
    
    if not success:
        print("=" * 60)
        print("CODE PROTECTION FAILED")
        print("=" * 60)
        print(f"ERROR: {message}")
        print("\nExecution blocked for security reasons.")
        print("=" * 60)
        sys.exit(1)
    
    # If hash was just injected, skip verification (file was just modified)
    # Only verify if hash already existed
    if "injected" not in message.lower():
        # Final verification (only if hash already existed)
        is_valid, verify_msg = verify_code_integrity(file_path)
        if not is_valid:
            print("=" * 60)
            print("CODE INTEGRITY VERIFICATION FAILED")
            print("=" * 60)
            print(f"ERROR: {verify_msg}")
            print("\nExecution blocked for security reasons.")
            print("=" * 60)
            sys.exit(1)


if __name__ == '__main__':
    main()
