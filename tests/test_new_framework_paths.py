import os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_default_data_and_site_are_nested():
    env=os.environ.copy();env.pop("SECOND_BRAIN_DATA_ROOT",None);env.pop("SECOND_BRAIN_SITE_ROOT",None)
    p=subprocess.run([sys.executable,str(ROOT/"scripts/repo_paths.py")],cwd=ROOT,env=env,capture_output=True,text=True)
    assert p.returncode==0
    assert f"DATA_ROOT={ROOT/'data'}" in p.stdout
    assert f"SITE_ROOT={ROOT/'site'}" in p.stdout
