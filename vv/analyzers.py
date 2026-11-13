from pathlib import Path
import re

RULES = [
    ("high", "Possible hard-coded credential", re.compile(r"""(?i)(api[_-]?key|secret|password|token)\s*=\s*['"][^'"]{8,}['"]"""), "Credential-like value in source."),
    ("high", "Use of eval()", re.compile(r"\beval\s*\("), "Dynamic code execution can introduce injection risk."),
    ("medium", "Use of shell=True", re.compile(r"\bshell\s*=\s*True"), "Shell command construction may be injectable."),
    ("low", "Debug print statement", re.compile(r"\bprint\s*\("), "Confirm this output is appropriate for production."),
    ("low", "TODO/FIXME marker", re.compile(r"\b(TODO|FIXME|XXX)\b"), "Potential unfinished implementation."),
]

def scan_repository(root, files):
    findings=[]
    for rel in files:
        try: lines=(Path(root)/rel).read_text(encoding="utf-8",errors="replace").splitlines()
        except OSError: continue
        for number,line in enumerate(lines,1):
            for severity,title,pattern,reason in RULES:
                if pattern.search(line):
                    findings.append({"severity":severity,"title":title,"file":rel,"line":number,"evidence":line.strip()[:240],"reason":reason,"source":"heuristic"})
                    break
            if len(findings)>=40: return findings
    return findings

def verify_finding(finding,root):
    rel=finding.get("file","")
    if not rel or Path(rel).is_absolute() or ".." in Path(rel).parts: return False,"Unsafe relative path."
    path=Path(root)/rel
    if not path.is_file(): return False,"File not found."
    lines=path.read_text(encoding="utf-8",errors="replace").splitlines()
    line=finding.get("line")
    if not isinstance(line,int) or line<1 or line>len(lines): return False,"Invalid line number."
    evidence=str(finding.get("evidence","")).strip()
    if evidence and evidence not in lines[line-1]: return False,"Evidence does not match source line."
    return True,"Evidence location verified; semantic impact still requires review."
