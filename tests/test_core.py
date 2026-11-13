from vv.scoring import score_finding, score_fix
from vv.analyzers import verify_finding, scan_repository
from vv.repository import inspect_repository, extract_zip, RepositoryError
from vv.patching import apply_unified_diff
import io, zipfile

def test_scoring():
    assert score_finding("critical",True)==25
    assert score_finding("low",False)==-10
    assert score_fix(1,True)==25
    assert score_fix(2,True)==20
    assert score_fix(3,False)==-5

def test_evidence(tmp_path):
    (tmp_path/"a.py").write_text("x = eval(user_input)\n")
    finding={"file":"a.py","line":1,"evidence":"x = eval(user_input)"}
    assert verify_finding(finding,tmp_path)[0]
    finding["evidence"]="wrong"
    assert not verify_finding(finding,tmp_path)[0]

def test_scanner(tmp_path):
    (tmp_path/"main.py").write_text("password = 'supersecretvalue'\neval(x)\n")
    info=inspect_repository(tmp_path)
    findings=scan_repository(tmp_path,info["files"])
    assert len(findings)>=2

def test_zip_traversal(tmp_path):
    data=io.BytesIO()
    with zipfile.ZipFile(data,"w") as z: z.writestr("../escape.txt","bad")
    data.seek(0)
    try: extract_zip(data,tmp_path/"out")
    except RepositoryError: pass
    else: assert False,"unsafe ZIP should be rejected"

def test_patch(tmp_path):
    (tmp_path/"hello.py").write_text("message = 'hello'\n")
    diff="""diff --git a/hello.py b/hello.py
--- a/hello.py
+++ b/hello.py
@@ -1 +1 @@
-message = 'hello'
+message = 'hello world'
"""
    ok,_=apply_unified_diff(tmp_path,diff)
    assert ok
    assert (tmp_path/"hello.py").read_text()=="message = 'hello world'\n"
