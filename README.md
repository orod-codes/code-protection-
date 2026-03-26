# Hash Injection Engine

**Author:** Dorsis Girma

A Python toolkit that **embeds cryptographic integrity checks** into source files across several languages. After protection, the code carries a **SHA-256 fingerprint** of the authorized content. If someone edits the protected sources (or related files where bundling applies), **startup/runtime verification fails** and execution is blocked.

Use it to ship **customer builds** that detect tampering, or to **audit** whether a tree of sources still matches what was injected.

---

## What it does (in plain terms)

1. **Inject** — Inserts special comment lines (`__HASH_INJECTED__`, `__LOCKED__`, optional recovery payload) and, for supported languages, a **runtime guard** that runs before your app logic.
2. **Lock** — The same file cannot be “re-injected” blindly; the engine detects an existing marker and stops (or treats removal as tampering, depending on mode).
3. **Verify** — On each run (or via CLI/UI), the guard recomputes a hash of the **canonical** source text and compares it to the value stored at injection time.
4. **Bundle related files** — For multi-file setups, integrity can include **sibling sources** in the same folder (e.g. other `.py` / `.js` / `.java` / `.cs`) or **C/C++ headers** next to a `.cpp`, so changing a dependency file also breaks the hash.

This is **software integrity / anti-tamper for source delivery**, not DRM and not a substitute for legal agreements or server-side enforcement.

---

## Supported languages

| Extension(s) | Runtime guard | Notes |
|--------------|---------------|--------|
| `.py` | Yes | Reads `__file__`, verifies on import. |
| `.js` | Yes (Node) | Top guard + **tail check** so the guard cannot be removed without detection. |
| `.java` | Yes | Resolves path vs **current working directory**; use folder mode paths when the project is nested. |
| `.cs` | Yes | Same cwd rules as Java for embedded relative paths. |
| `.cpp`, `.cc`, `.cxx` | Yes (OpenSSL) | Link with **`-lcrypto`**. Hashes **same-dir headers** listed in `__EI_HDRS__`. |
| `.c`, `.h`, … | Partial | C uses an OpenSSL-based guard where injected; headers may be processed per engine rules. |
| `.php` | Markers / integrity | PHP flow differs from in-process guards on other runtimes. |

Exact extension sets are defined in `engine.py` as `SUPPORTED_LANGUAGE_EXTENSIONS`.

---

## Requirements

- **Python 3** (3.9+ recommended)
- **Flask** — only if you use the web UI: `pip install flask`
- **OpenSSL development libraries** — for **C/C++** guarded builds (`libcrypto`), e.g. `libssl-dev` on Debian/Ubuntu

---

## Installation

```bash
git clone <your-repo-url>
cd <repo-folder>
pip install flask   # optional, for web_injector.py
```

The main CLI is **`engine.py`** at the repository root.  
(Optional) A copy may exist under `check-one/universal_profile_app/` for demos—prefer the **root** `engine.py` as the canonical version.

---

## Inject & check (short)

Run all commands from the folder that contains `engine.py` (or pass the full path to `engine.py`).

### Single file

| What you want | Command |
|---------------|---------|
| **Inject** — change the file in place (adds hash + runtime guard) | `python3 engine.py path/to/app.py` |
| **Inject** — write a **new** protected file; original stays untouched | `python3 engine.py path/to/app.py --generate` |
| **Check** — already protected? Re-verify hash; if not protected, inject first | `python3 engine.py path/to/app.py --auto` |
| **Check** — only by running the app | Run `python3 app.py` (or your language’s runner); the guard runs first and exits if the code was tampered with |

### Folder

| What you want | Command |
|---------------|---------|
| **Inject** — copy the whole tree to `<folder>_customer` (recommended for delivery) | `python3 engine.py ./my_project --generate-folder` |
| **Inject** — custom output folder name | `python3 engine.py ./my_project --generate-folder ./my_project_customer` |
| **Inject** — protect **inside** the folder you pass (files modified in place) | `python3 engine.py ./my_project` *(same as* `--auto` *)* |
| **Check** — scan every supported file under the folder | `python3 engine.py ./my_project --verify` |

**Summary:** one file → `engine.py <file>` to inject, `--generate` for a copy, `--auto` to verify or inject. One folder → `--generate-folder` for a customer copy, bare folder path or `--auto` to patch in place, `--verify` to audit.

---

## Quick start

### Protect a single file (inject in place)

```bash
python3 engine.py path/to/app.py
```

### Auto-protect (inject if needed, or verify if already injected)

```bash
python3 engine.py path/to/app.py --auto
```

### Protect and run (Python only)

```bash
python3 engine.py path/to/app.py --run
```

### Generate a **separate** customer file (original unchanged)

```bash
python3 engine.py path/to/app.py --generate
# or explicit output:
python3 engine.py path/to/app.py --generate path/to/app.customer.py
```

### Protect an entire **folder** (customer copy)

Creates `<folder>_customer` with the same structure and injected sources:

```bash
python3 engine.py ./my_project --generate-folder
python3 engine.py ./my_project --generate-folder ./my_project_customer
```

For **Java / C#** customer trees, run the app with the **customer folder** as the **current working directory** so embedded relative paths resolve correctly.

### Verify all supported files in a folder

```bash
python3 engine.py ./my_project --verify
```

### Development only: strip markers (use with care)

```bash
python3 engine.py ./my_project --dev-reset
```

### Show stored original vs current (for debugging)

```bash
python3 engine.py path/to/protected.py --show-codes
```

---

## How injection works (technical)

1. **Runtime guard insertion** (where supported)  
   Language-specific code is prepended (and for JS, a tail check appended) so that **before** your program continues, it:
   - reads the protected source from disk,
   - finds the `__HASH_INJECTED__:` line and reads the **stored code hash**,
   - rebuilds the **canonical** text (excluding marker / lock / record lines, sibling manifest lines, etc., per language),
   - optionally appends **bundled** neighbor files (same-folder siblings or C++ header bodies),
   - computes **SHA-256** and compares to the stored value.

2. **Marker lines** (after the first line of the file)  
   - `__HASH_INJECTED__:` — holds injection id, **code hash**, and (optionally) gzip+base64 of the pre-marker content for recovery/diff.  
   - `__LOCKED__:` — lock fingerprint.  
   - `__INJECTION_RECORD__:` — may record tamper / lock state depending on engine paths.

3. **One-shot injection**  
   If a valid injection is already present, the engine **refuses** to inject again, avoiding accidental double markers.

4. **C++ headers**  
   Manifest comment `// __EI_HDRS__: ...` lists headers in the **same directory** as the `.cpp`; their contents participate in the hash.

5. **Python / JS / Java / C# siblings**  
   Manifest `# __EI_SIB__:` or `// __EI_SIB__:` lists **other** source files in the **same directory** (by extension rules). Changing any of them invalidates the hash unless you re-protect.

Legacy files **without** `__EI_SIB__` / `__EI_HDRS__` behave like **single-file** hashes for backward compatibility.

---

## Web UI (`web_injector.py`)

Browser workflow: upload a **source file** or a **ZIP** project.

```bash
pip install flask
python3 web_injector.py
# Open http://127.0.0.1:5000 (see terminal for actual port)
```

Typical actions:

- **Inject** — Produce a `.customer` file or a `.customer.zip` with protected sources.  
- **Reverse** — Restore embedded original from the marker where possible.  
- **Verify** — Health report (single file or ZIP with `health_report.txt`).

History is stored locally in `.web_history.json` (gitignore it if you publish a fork).

---

## Example projects

Under `check-one/`:

| Path | Description |
|------|-------------|
| `universal_profile_app/` | Same “User + BMI” layout in **Python, Java, Node, C++, C#, PHP**. |
| `simple_project/` | Small dependent Python package. |
| `full_test_app/` | Larger Python sample. |

See `check-one/DEMO_PROJECTS.txt` for one-liners.

---

## How to run the code (all languages)

Assume you are in the **repository root** (the folder that contains `engine.py`). Replace `/path/to/repo` if you keep the project elsewhere.

### Engine & web UI (Python)

| What | Command |
|------|---------|
| Engine CLI (inject / verify / etc.) | `python3 engine.py` *(see [Inject & check](#inject--check-short))* |
| Web injector | `pip install flask` then `python3 web_injector.py` → open `http://127.0.0.1:5000` |

### Single file at repo root (example)

| What | Command |
|------|---------|
| Hello-world script | `python3 testpython.py` |

### Demo: `check-one/universal_profile_app/` (User + BMI sample)

Use **`cd`** into each language folder first so imports / paths work.

| Language | Commands |
|----------|----------|
| **Python** | `cd check-one/universal_profile_app/python` then `python3 main.py` |
| **JavaScript (Node)** | `cd check-one/universal_profile_app/node` then `node main.js` |
| **Java** | `cd check-one/universal_profile_app/java` then `javac -d out src/model/User.java src/service/BMIService.java src/util/InputUtil.java src/Main.java` then `java -cp out Main` |
| **C++** | `cd check-one/universal_profile_app/cpp` then `g++ -std=c++17 -o app main.cpp` then `./app` |
| **C# (Mono)** | `cd check-one/universal_profile_app/csharp` then `mcs -out:app.exe Models/User.cs Services/BMIService.cs Utils/ConsoleUtil.cs Program.cs` then `mono app.exe` |
| **C# (.NET SDK)** | `cd check-one/universal_profile_app/csharp` — create/use a console project that includes those `.cs` files, then `dotnet run` |
| **PHP** (CLI; needs `readline`) | `cd check-one/universal_profile_app/php` then `php index.php` |

**C** (supported by the engine; no sample app in `universal_profile_app`): compile your `.c` files with `gcc`, e.g. `gcc -std=c11 -o app main.c` then `./app`. After injection, add **`-lcrypto`** if the guard uses OpenSSL.

One-liner style from repo root (non-interactive test with piped input):

```bash
printf 'Ada\n30\n70\n170\n' | python3 check-one/universal_profile_app/python/main.py
printf 'Ada\n30\n70\n170\n' | node check-one/universal_profile_app/node/main.js
printf 'Ada\n30\n70\n170\n' | php check-one/universal_profile_app/php/index.php
```

### Demo: `check-one/simple_project/` (Python only)

| Command |
|---------|
| `cd check-one/simple_project && python3 main.py` |

### Demo: `check-one/full_test_app/` (Python only)

| Command |
|---------|
| `cd check-one/full_test_app && python3 main.py` |

### C / C++ after **hash injection** (OpenSSL guard)

If the engine embedded the C/C++ runtime guard, link **libcrypto**:

```bash
g++ -std=c++17 -o app main.cpp -lcrypto
gcc -o app main.c other.c -lcrypto
```

### Java / C# **customer folder** builds

If you used `--generate-folder`, run programs with the **customer folder** as the **current working directory** so embedded relative paths resolve, for example:

```bash
cd my_project_customer
java -cp java/out Main
```

---

## Project layout (reference)

```text
engine.py           # CLI + core: inject, verify, generate, folder modes
web_injector.py     # Flask UI (ZIP / single file)
templates/          # Web templates
check-one/          # Demos and optional bundled engine copy for samples
```

---

## Limitations & ethics

- Protects **honest** customers from **casual** or **accidental** source edits; a determined attacker can still reverse or patch binaries, strip guards, or run modified copies if they control the environment.
- **Secrets** do not belong in client-side source; this tool does not replace secure key management or server-side authorization.
- Use **`--dev-reset`** only in trusted development contexts.

---

## Contributing

Issues and PRs are welcome. Please keep changes focused and match existing style in `engine.py`.

---

## License

Specify your license here (e.g. MIT). If you do not add a `LICENSE` file, default copyright applies.

---

*Project by Dorsis Girma.*
