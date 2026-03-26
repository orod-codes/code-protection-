#!/usr/bin/env python3
"""Web injector UI with ZIP-in / ZIP-out workflow."""

import base64
import datetime
import gzip
import json
import os
import zipfile
import tempfile
import uuid
from typing import Optional, List

from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from engine import (
    SUPPORTED_LANGUAGE_EXTENSIONS,
    generate_injected_file,
    iter_supported_files,
    verify_code_integrity,
)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, ".web_uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, ".web_outputs")
HISTORY_FILE = os.path.join(BASE_DIR, ".web_history.json")
MAX_HISTORY_ITEMS = 50

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = Flask(__name__)


def _allowed_source(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in SUPPORTED_LANGUAGE_EXTENSIONS or ext == ".zip"


def _build_customer_name(input_name: str) -> str:
    root, ext = os.path.splitext(input_name)
    return f"{root}.customer{ext}"


def _build_restored_name(input_name: str) -> str:
    root, ext = os.path.splitext(input_name)
    if root.endswith(".customer"):
        root = root[: -len(".customer")]
    return f"{root}.restored{ext}"


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _safe_extract_zip(zip_path: str, extract_dir: str) -> None:
    """Extract zip while blocking path traversal."""
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            member_name = member.filename.replace("\\", "/")
            if member_name.startswith("/") or ".." in member_name.split("/"):
                raise ValueError(f"Unsafe zip entry: {member.filename}")
        zf.extractall(extract_dir)


def _inject_folder_in_place(folder_path: str) -> List[str]:
    """
    Inject all supported source files in place.

    Returns a list of relative file paths that were protected.
    """
    protected: List[str] = []
    files = iter_supported_files(folder_path, include_engine=True)
    for file_path in files:
        temp_out = f"{file_path}.customer_build{os.path.splitext(file_path)[1]}"
        ok, msg = generate_injected_file(file_path, temp_out)
        if not ok:
            raise RuntimeError(f"Failed on {os.path.basename(file_path)}: {msg}")
        os.replace(temp_out, file_path)
        protected.append(os.path.relpath(file_path, folder_path))
    return protected


def _extract_original_code(file_path: str) -> str:
    marker = "__HASH_INJECTED__:"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    for line in content.split("\n"):
        stripped = line.strip()
        if marker not in stripped:
            continue

        parts = stripped.split(marker, 1)[1].strip().split()
        if len(parts) < 3:
            raise RuntimeError("No embedded original code found in marker.")
        encoded = parts[2]
        try:
            compressed = base64.b64decode(encoded.encode("utf-8"))
            original_bytes = gzip.decompress(compressed)
            return original_bytes.decode("utf-8")
        except Exception as exc:
            raise RuntimeError(f"Failed to decode embedded original code: {exc}") from exc

    raise RuntimeError("Injection marker not found.")


def _reverse_file_in_place(file_path: str) -> None:
    original = _extract_original_code(file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(original)


def _reverse_folder_in_place(folder_path: str) -> List[str]:
    reversed_files: List[str] = []
    files = iter_supported_files(folder_path, include_engine=True)
    for file_path in files:
        try:
            _reverse_file_in_place(file_path)
            reversed_files.append(os.path.relpath(file_path, folder_path))
        except Exception:
            # Skip files that are not injected.
            continue
    if not reversed_files:
        raise RuntimeError("No injected files found to reverse.")
    return reversed_files


def _verify_folder_health(folder_path: str) -> str:
    """
    Verify integrity of all supported files in a folder and return a human summary.
    """
    files = iter_supported_files(folder_path, include_engine=True)
    if not files:
        return "No supported source files found."

    ok_count = 0
    fail_count = 0
    no_hash_count = 0
    details: List[str] = []

    for file_path in files:
        rel = os.path.relpath(file_path, folder_path)
        valid, message = verify_code_integrity(file_path)
        if valid:
            ok_count += 1
            details.append(f"[OK] {rel}")
            continue

        lower_msg = message.lower()
        if "no hash found" in lower_msg:
            no_hash_count += 1
            details.append(f"[NO_HASH] {rel}: {message}")
        else:
            fail_count += 1
            details.append(f"[MODIFIED] {rel}: {message}")

    total = len(files)
    score = (ok_count / total) * 100 if total else 0.0
    header = (
        f"Health score: {score:.1f}%\n"
        f"Total files: {total}\n"
        f"Verified OK: {ok_count}\n"
        f"Modified/Tampered: {fail_count}\n"
        f"Not injected: {no_hash_count}\n"
    )
    return header + "\nDetails:\n" + "\n".join(details[:120]) + (
        "\n... more entries omitted ..." if len(details) > 120 else ""
    )


def _extract_changed_lines_section(message: str) -> str:
    """
    Return only line-level change details from integrity message when available.
    """
    marker = "Changed lines:"
    idx = message.find(marker)
    if idx >= 0:
        return message[idx:].strip()
    return ""


def _verify_single_health(file_path: str) -> str:
    """
    Single-file health summary focused on where code changed.
    """
    valid, message = verify_code_integrity(file_path)
    if valid:
        return "Health score: 100%\nStatus: VERIFIED\n\nCode integrity verified."

    lower = message.lower()
    if "no hash found" in lower:
        return "Health score: 0%\nStatus: NOT INJECTED\n\nNo injected hash marker found."

    if "hash marker missing" in lower or "manually deleted" in lower:
        return (
            "Health score: 0%\nStatus: TAMPERED\n\n"
            "Hash marker was removed manually."
        )

    changed_only = _extract_changed_lines_section(message)
    if changed_only:
        return f"Health score: 0%\nStatus: MODIFIED\n\n{changed_only}"

    # Fallback for runtimes that don't provide line-by-line info.
    return (
        "Health score: 0%\nStatus: MODIFIED\n\n"
        "Change detected, but exact changed lines are not available for this file type."
    )


def _zip_directory(source_dir: str, output_zip_path: str) -> None:
    with zipfile.ZipFile(output_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(source_dir):
            for filename in files:
                full_path = os.path.join(root, filename)
                arcname = os.path.relpath(full_path, source_dir)
                zf.write(full_path, arcname)


def _load_history() -> List[dict]:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def _save_history(items: List[dict]) -> None:
    trimmed = items[:MAX_HISTORY_ITEMS]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(trimmed, f, indent=2)


def _append_history(action: str, input_name: str, status: str, message: str, output_name: str = "") -> None:
    items = _load_history()
    items.insert(
        0,
        {
            "time": datetime.datetime.now().isoformat(timespec="seconds"),
            "action": action,
            "input": input_name,
            "status": status,
            "output": output_name,
            "message": message[:400],
        },
    )
    _save_history(items)


@app.route("/", methods=["GET", "POST"])
def index():
    error: Optional[str] = None
    output_stored_name: Optional[str] = None
    output_filename: Optional[str] = None
    source_preview = ""
    result_summary = ""
    action = "inject"

    if request.method == "POST":
        action = request.form.get("action", "inject").strip().lower()
        if action not in ("inject", "reverse", "verify"):
            action = "inject"

        file_obj = request.files.get("source_file")
        if file_obj is None or file_obj.filename.strip() == "":
            error = "Please choose a source file first."
        else:
            incoming_name = secure_filename(file_obj.filename)
            if not incoming_name:
                error = "Invalid filename."
            elif not _allowed_source(incoming_name):
                error = "Unsupported file. Upload a source file or a .zip project."
            else:
                upload_name = f"{uuid.uuid4().hex}_{incoming_name}"
                upload_path = os.path.join(UPLOAD_DIR, upload_name)
                file_obj.save(upload_path)

                ext = os.path.splitext(incoming_name)[1].lower()
                try:
                    if ext == ".zip":
                        with tempfile.TemporaryDirectory(prefix="web_inject_") as tmp_dir:
                            extracted_dir = os.path.join(tmp_dir, "project")
                            os.makedirs(extracted_dir, exist_ok=True)
                            _safe_extract_zip(upload_path, extracted_dir)

                            if action == "verify":
                                output_filename = f"{os.path.splitext(incoming_name)[0]}.health.zip"
                                output_stored_name = f"{uuid.uuid4().hex}_{output_filename}"
                                output_zip_path = os.path.join(OUTPUT_DIR, output_stored_name)
                                source_preview = f"Uploaded ZIP: {incoming_name}"
                                result_summary = _verify_folder_health(extracted_dir)
                                with zipfile.ZipFile(output_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                                    zf.writestr("health_report.txt", result_summary)
                            else:
                                suffix = "customer" if action == "inject" else "restored"
                                output_filename = f"{os.path.splitext(incoming_name)[0]}.{suffix}.zip"
                                output_stored_name = f"{uuid.uuid4().hex}_{output_filename}"
                                output_zip_path = os.path.join(OUTPUT_DIR, output_stored_name)

                                if action == "inject":
                                    processed_files = _inject_folder_in_place(extracted_dir)
                                else:
                                    processed_files = _reverse_folder_in_place(extracted_dir)

                                _zip_directory(extracted_dir, output_zip_path)
                                source_preview = f"Uploaded ZIP: {incoming_name}"
                                if processed_files:
                                    joined = "\n".join(f"- {p}" for p in processed_files[:80])
                                    if len(processed_files) > 80:
                                        joined += "\n- ... more files ..."
                                    title = "Protected files" if action == "inject" else "Reversed files"
                                    result_summary = (
                                        f"{title}: {len(processed_files)}\n\n"
                                        f"{joined}"
                                    )
                                else:
                                    result_summary = "No supported source files were processed."
                    else:
                        if action == "verify":
                            output_filename = f"{os.path.splitext(incoming_name)[0]}.health.zip"
                            output_stored_name = f"{uuid.uuid4().hex}_{output_filename}"
                            output_zip_path = os.path.join(OUTPUT_DIR, output_stored_name)
                            source_preview = _read_text(upload_path)
                            result_summary = _verify_single_health(upload_path)
                            with zipfile.ZipFile(output_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                                zf.writestr("health_report.txt", result_summary)
                        else:
                            if action == "inject":
                                output_inner_name = _build_customer_name(incoming_name)
                                output_filename = f"{os.path.splitext(incoming_name)[0]}.customer.zip"
                            else:
                                output_inner_name = _build_restored_name(incoming_name)
                                output_filename = f"{os.path.splitext(incoming_name)[0]}.restored.zip"

                            output_stored_name = f"{uuid.uuid4().hex}_{output_filename}"
                            output_zip_path = os.path.join(OUTPUT_DIR, output_stored_name)

                            with tempfile.TemporaryDirectory(prefix="web_inject_single_") as tmp_dir:
                                generated_path = os.path.join(tmp_dir, output_inner_name)
                                if action == "inject":
                                    ok, message = generate_injected_file(upload_path, generated_path)
                                    if not ok:
                                        raise RuntimeError(message)
                                else:
                                    with open(upload_path, "r", encoding="utf-8") as src_f:
                                        source_preview = src_f.read()
                                    original = _extract_original_code(upload_path)
                                    with open(generated_path, "w", encoding="utf-8") as out_f:
                                        out_f.write(original)

                                with zipfile.ZipFile(output_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                                    zf.write(generated_path, output_inner_name)

                                if action == "inject":
                                    source_preview = _read_text(upload_path)
                                    result_summary = (
                                        f"Generated protected file: {output_inner_name}\n"
                                        "Packaged as ZIP output."
                                    )
                                else:
                                    result_summary = (
                                        f"Restored original file: {output_inner_name}\n"
                                        "Packaged as ZIP output."
                                    )
                except Exception as exc:
                    error = str(exc)
                    output_stored_name = None
                    output_filename = None
                    _append_history(action, incoming_name, "error", error)
                else:
                    _append_history(
                        action,
                        incoming_name,
                        "success",
                        result_summary if result_summary else "Completed",
                        output_filename if output_filename else "",
                    )

    return render_template(
        "index.html",
        error=error,
        output_stored_name=output_stored_name,
        output_filename=output_filename,
        source_preview=source_preview,
        result_summary=result_summary,
        action=action,
        history_items=_load_history()[:12],
    )


@app.route("/download/<path:stored_name>", methods=["GET"])
def download(stored_name: str):
    return send_from_directory(
        OUTPUT_DIR,
        stored_name,
        as_attachment=True,
        download_name="_".join(stored_name.split("_")[1:]) if "_" in stored_name else stored_name,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

