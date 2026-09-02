from __future__ import annotations
import os,shutil,subprocess,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1];SCRIPTS=ROOT/"scripts";FIXTURE=ROOT/"tests"/"fixtures"/"mini-brain"

def run_script(name,*args,data_root=None,site_root=None,timeout=120):
    env=os.environ.copy()
    if data_root is not None: env["SECOND_BRAIN_DATA_ROOT"]=str(data_root)
    if site_root is not None: env["SECOND_BRAIN_SITE_ROOT"]=str(site_root)
    return subprocess.run([sys.executable,str(SCRIPTS/name),*args],cwd=ROOT,env=env,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=timeout)

def recursive_severities(obj):
    out=[]
    if isinstance(obj,dict):
        sev=str(obj.get("severity","")).upper()
        if sev: out.append((sev,obj.get("code")))
        for v in obj.values(): out.extend(recursive_severities(v))
    elif isinstance(obj,list):
        for v in obj: out.extend(recursive_severities(v))
    return out

@pytest.fixture
def mini_brain(tmp_path):
    target=tmp_path/"mini-brain";shutil.copytree(FIXTURE,target)
    for sub in ("html","pdf","handouts","stats","graph"):
        (target/"output"/sub).mkdir(parents=True,exist_ok=True)
    return target

@pytest.fixture
def installed_mini_brain(tmp_path,monkeypatch):
    target=tmp_path/"installed-mini-brain";shutil.copytree(FIXTURE,target)
    for sub in ("html","pdf","handouts","stats","graph"):
        (target/"output"/sub).mkdir(parents=True,exist_ok=True)
    monkeypatch.setenv("SECOND_BRAIN_DATA_ROOT",str(target))
    # Critical safety property: tests never install fixtures under the real
    # engine root or the real nested data/ repository.
    yield target

def legacy_script_available(name,min_bytes=500):
    p=SCRIPTS/name
    return p.exists() and p.stat().st_size>=min_bytes
