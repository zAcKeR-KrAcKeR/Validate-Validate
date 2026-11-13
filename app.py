from __future__ import annotations
import json, os, tempfile
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from vv.agents import AgentClient, assess_finding, generate_task, implement_task, review_repository
from vv.analyzers import scan_repository, verify_finding
from vv.patching import apply_unified_diff
from vv.repository import RepositoryError, clone_repository, extract_zip, inspect_repository
from vv.scoring import score_finding

load_dotenv()
st.set_page_config(page_title="Validate Validate", page_icon="⚔️", layout="wide")
st.title("⚔️ Validate Validate")
st.caption("AI builds. AI challenges. Evidence decides.")
for k,v in {"repo_root":None,"repo_info":None,"score":{"developer":0,"validator":0},"history":[],"findings":[],"task":None,"fixes":{},"round":0,"workspace":None,"repo_label":"No repository loaded","task_patch":None}.items():
    if k not in st.session_state: st.session_state[k]=v

def client(role):
    model=os.getenv("OPENAI_"+role.upper()+"_MODEL",os.getenv("OPENAI_MODEL","gpt-4.1-mini"))
    return AgentClient(api_key=st.session_state.get("api_key","") or os.getenv("OPENAI_API_KEY",""),model=st.session_state.get(role+"_model","") or model,base_url=st.session_state.get("base_url","") or os.getenv("OPENAI_BASE_URL") or None)

def load_repo(path,label):
    info=inspect_repository(path)
    if not info["files"]: raise RepositoryError("No supported source files found.")
    for k,v in {"repo_root":str(path),"repo_info":info,"repo_label":label,"findings":[],"task":None,"task_patch":None,"fixes":{},"history":[],"round":0,"score":{"developer":0,"validator":0}}.items(): st.session_state[k]=v

with st.sidebar:
    st.header("Game controls")
    url=st.text_input("Public GitHub HTTPS URL",placeholder="https://github.com/owner/repo")
    if st.button("Clone repository",disabled=not url.strip()):
        try:
            work=Path(tempfile.mkdtemp(prefix="vv-"))/"repo"
            load_repo(clone_repository(url,work),url); st.session_state.workspace=str(work.parent); st.success("Repository loaded.")
        except Exception as e: st.error(str(e))
    upload=st.file_uploader("Or upload repository ZIP",type=["zip"])
    if st.button("Load ZIP",disabled=upload is None):
        try:
            work=Path(tempfile.mkdtemp(prefix="vv-")); load_repo(extract_zip(upload,work),upload.name); st.session_state.workspace=str(work); st.success("ZIP loaded.")
        except Exception as e: st.error(str(e))
    st.divider(); st.subheader("AI configuration")
    st.text_input("API key",type="password",key="api_key")
    st.text_input("Developer model",value=os.getenv("OPENAI_DEVELOPER_MODEL",os.getenv("OPENAI_MODEL","gpt-4.1-mini")),key="developer_model")
    st.text_input("Validator model",value=os.getenv("OPENAI_VALIDATOR_MODEL",os.getenv("OPENAI_MODEL","gpt-4.1-mini")),key="validator_model")
    st.text_input("OpenAI-compatible base URL",value=os.getenv("OPENAI_BASE_URL",""),key="base_url")
    st.caption("Leave API key blank for deterministic demo mode. Repository code is inspected as text; it is never executed.")

m=st.columns(3); m[0].metric("Developer points",st.session_state.score["developer"]); m[1].metric("Validator points",st.session_state.score["validator"]); m[2].metric("Rounds",st.session_state.round)
if not st.session_state.repo_info:
    st.info("Load a public GitHub repository or upload a ZIP to start.")
    st.markdown("### How a round works\n1. Developer Agent proposes a task.\n2. Validator Agent finds defects and cites exact evidence.\n3. Developer accepts or disputes each finding.\n4. Review a proposed patch and explicitly apply it.")
    st.stop()
repo=st.session_state.repo_info; dev=client("developer"); val=client("validator")
st.success(f"Loaded **{st.session_state.repo_label}** · {repo['file_count']} source files")
if repo["truncated"]: st.warning("Model source context was capped.")
game,inventory,history,rules=st.tabs(["🎮 Game arena","📁 Repository","📜 History","🏆 Rules"])
with game:
    a,b=st.columns(2)
    with a:
        st.subheader("Developer Agent")
        if st.button("Generate development task",type="primary"):
            try: st.session_state.task=generate_task(dev,repo); st.session_state.round+=1
            except Exception as e: st.error(str(e))
        if st.session_state.task:
            task=st.session_state.task; st.markdown("### "+task.get("title","Task")); st.write(task.get("objective",""))
            for x in task.get("acceptance_criteria",[]): st.markdown("- "+x)
            if st.button("Implement task",disabled=not dev.enabled):
                st.session_state.task_patch=implement_task(dev,task,repo)
            patch=st.session_state.task_patch
            if patch:
                st.write(patch.get("summary","")); diff=patch.get("unified_diff","")
                if diff:
                    st.code(diff,language="diff")
                    if st.button("Apply implementation patch"):
                        ok,msg=apply_unified_diff(repo["root"],diff)
                        if ok: st.session_state.score["developer"]+=15; st.session_state.repo_info=inspect_repository(repo["root"]); st.success(msg)
                        else: st.error(msg)
    with b:
        st.subheader("Validator Agent")
        if st.button("Run adversarial review"):
            try:
                static=scan_repository(repo["root"],repo["files"])
                found=review_repository(val,repo,static)
                for f in found:
                    ok,note=verify_finding(f,repo["root"]); f["evidence_location_verified"]=ok; f["verification_note"]=note; f.setdefault("status","candidate")
                st.session_state.findings=found
            except Exception as e: st.error(str(e))
        st.caption("Demo mode findings are heuristic candidates, not confirmed bugs.")
    st.divider(); st.subheader("Findings")
    if not st.session_state.findings: st.caption("Run the Validator Agent to inspect source.")
    for i,f in enumerate(st.session_state.findings):
        with st.expander(f"{f.get('severity','low').upper()} · {f.get('title','Finding')} · {f.get('file','?')}:{f.get('line','?')}"):
            st.write(f.get("reason","")); st.code(f.get("evidence","")); st.write("Impact:",f.get("impact","Not assessed")); st.write("Verification:",f.get("verification_note",""))
            if not f.get("evidence_location_verified"): st.error("Evidence location failed verification.")
            c1,c2=st.columns(2)
            if c1.button("Submit to developer",key=f"submit{i}",disabled=not f.get("evidence_location_verified") or f.get("status") in ("submitted","accepted","rejected","fixed","disputed")):
                f["status"]="submitted"; st.rerun()
            if c2.button("Reject false positive",key=f"reject{i}",disabled=f.get("status") in ("submitted","accepted","rejected","fixed","disputed")):
                f["status"]="rejected"; p=score_finding(f.get("severity","low"),False); st.session_state.score["validator"]+=p; st.rerun()
            if f.get("status")=="submitted" and st.button("Developer: assess finding",key=f"assess{i}"):
                response=assess_finding(dev,f,repo); st.session_state.fixes[str(i)]=response
                if response.get("accepted"):
                    f["status"]="accepted"; st.session_state.score["validator"]+=score_finding(f.get("severity","low"),True)
                else: f["status"]="disputed"
                st.rerun()
            fix=st.session_state.fixes.get(str(i))
            if fix:
                st.write(fix.get("assessment","")); st.write("Fix plan:",fix.get("fix_plan",[])); diff=fix.get("unified_diff","")
                if diff:
                    st.code(diff,language="diff")
                    if st.button("Apply reviewed fix",key=f"apply{i}",disabled=f.get("status")!="accepted"):
                        ok,msg=apply_unified_diff(repo["root"],diff)
                        if ok: f["status"]="fixed"; st.session_state.score["developer"]+=15; st.session_state.repo_info=inspect_repository(repo["root"]); st.success(msg)
                        else: st.error(msg)
with inventory:
    st.write("Repository root:",repo["root"]); st.dataframe([{"file":x,"extension":Path(x).suffix} for x in repo["files"]],use_container_width=True)
    if st.button("Refresh inspection"): st.session_state.repo_info=inspect_repository(repo["root"]); st.rerun()
with history:
    st.dataframe(st.session_state.history,use_container_width=True)
    st.download_button("Download score report",json.dumps({"score":st.session_state.score,"history":st.session_state.history},indent=2),file_name="validate-validate-report.json")
with rules:
    st.markdown("| Event | Points |\n|---|---:|\n| Accepted low/medium/high/critical finding | +5/+10/+15/+25 Validator |\n| Rejected false positive | -10 Validator |\n| Successful first patch | +15 Developer |\n| Regression tests | Not run automatically |")
    st.warning("Evidence-location checks do not prove semantic correctness. Review patches before applying. This MVP does not execute untrusted repository code or tests.")
