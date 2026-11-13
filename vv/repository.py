from pathlib import Path
import os, re, shutil, subprocess, zipfile

ALLOWED = {".py",".js",".jsx",".ts",".tsx",".java",".go",".rs",".rb",".php",".cs",".cpp",".c",".h",".sql",".yaml",".yml",".toml",".json",".md",".sh"}
SKIP = {".git","node_modules",".venv","venv","dist","build","__pycache__",".next","vendor"}

class RepositoryError(Exception): pass

def extract_zip(uploaded_file, destination):
    root = Path(destination).resolve()
    root.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(uploaded_file) as z:
            for item in z.infolist():
                dest = (root / item.filename).resolve()
                if root not in dest.parents and dest != root:
                    raise RepositoryError("Unsafe ZIP path traversal.")
            z.extractall(root)
    except zipfile.BadZipFile as e:
        raise RepositoryError("Invalid ZIP archive.") from e
    children = [p for p in root.iterdir() if p.is_dir()]
    files = [p for p in root.iterdir() if p.is_file()]
    return children[0] if len(children) == 1 and not files else root

def clone_repository(url, destination):
    if not re.match(r"^https://github\\.com/[\\w.-]+/[\\w.-]+(?:\\.git)?/?$", url.strip()):
        raise RepositoryError("Use a public GitHub HTTPS URL.")
    p = subprocess.run(["git","clone","--depth","1",url.strip(),str(destination)],capture_output=True,text=True,timeout=90)
    if p.returncode: raise RepositoryError((p.stderr or p.stdout)[-1200:])
    return Path(destination)

def inspect_repository(root, max_files=80, max_chars=24000):
    root=Path(root); files=[]; chunks=[]; total=0
    for current, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for name in sorted(names):
            path=Path(current)/name; rel=path.relative_to(root).as_posix()
            if path.suffix.lower() not in ALLOWED or re.search(r"(^|/)(\\.env|id_rsa|credentials\\.json|secrets?\\.ya?ml)$",rel,re.I): continue
            if path.stat().st_size > 80000: continue
            files.append(rel)
            try: body=path.read_text(encoding="utf-8",errors="replace")
            except OSError: continue
            body=body[:max(0,max_chars-total)]
            if body.strip(): chunks.append(f"\\n--- FILE: {rel} ---\\n{body}"); total+=len(body)
            if len(files)>=max_files or total>=max_chars: break
        if len(files)>=max_files or total>=max_chars: break
    return {"root":str(root),"files":files,"file_count":len(files),"context":"\\n".join(chunks),"truncated":total>=max_chars}
