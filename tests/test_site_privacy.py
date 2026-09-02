import json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def mk(path,title,pub,body="Corpo."):
    path.write_text(f"---\ntags: [Teste]\ncreated: 2026-01-01\nupdated: 2026-01-01\nsummary: resumo\nstatus: draft\npublish: {'true' if pub else 'false'}\n---\n# {title}\n\n{body}\n",encoding="utf-8")
def test_public_site_is_allowlist_and_private_identity_does_not_leak(tmp_path):
    data=tmp_path/"data";site=tmp_path/"site";d=data/"wiki"/"essays";d.mkdir(parents=True);site.mkdir()
    (site/".second-brain-site").write_text("marker",encoding="utf-8")
    mk(d/"dutch-roll.md","Dutch Roll",True,"Texto público. [[segredo-ultra-privado|conceito interno]].\n\n## Conexões\n- [[segredo-ultra-privado|SEGREDO ULTRA PRIVADO]]")
    mk(d/"segredo-ultra-privado.md","SEGREDO ULTRA PRIVADO",False,"SENTINELA_PRIVADA_49A1")
    env=os.environ.copy();env["SECOND_BRAIN_DATA_ROOT"]=str(data);env["SECOND_BRAIN_SITE_ROOT"]=str(site)
    b=subprocess.run([sys.executable,str(ROOT/"scripts/build_site.py"),"--no-render"],cwd=ROOT,env=env,capture_output=True,text=True)
    assert b.returncode==0,b.stdout+b.stderr
    combined="\n".join(p.read_text(encoding="utf-8",errors="ignore") for p in site.rglob("*") if p.is_file())
    assert "SENTINELA_PRIVADA_49A1" not in combined
    assert "segredo-ultra-privado" not in combined
    assert "SEGREDO ULTRA PRIVADO" not in combined
    graph=json.loads((site/"graph.json").read_text(encoding="utf-8"))
    assert [n["id"] for n in graph["nodes"]]==["dutch-roll"]
    c=subprocess.run([sys.executable,str(ROOT/"scripts/check_site_privacy.py"),"--json"],cwd=ROOT,env=env,capture_output=True,text=True)
    assert c.returncode==0,c.stdout+c.stderr
