from pathlib import Path
import subprocess

def apply_unified_diff(root, diff):
    root=Path(root)
    if not diff.strip() or "diff --git" not in diff or "../" in diff or "\\x00" in diff:
        return False, "Unsafe or empty unified diff."
    if not (root/".git").exists():
        subprocess.run(["git","init",str(root)],capture_output=True,text=True,timeout=10)
    check=subprocess.run(["git","apply","--check","-"],input=diff,cwd=root,capture_output=True,text=True,timeout=15)
    if check.returncode: return False,(check.stderr or check.stdout)[-1000:]
    done=subprocess.run(["git","apply","-"],input=diff,cwd=root,capture_output=True,text=True,timeout=15)
    return (done.returncode==0, "Patch applied; run tests and review changes." if done.returncode==0 else (done.stderr or done.stdout)[-1000:])
