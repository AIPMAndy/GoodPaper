from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_docs_do_not_exaggerate_features():
    readme=(ROOT/"README.md").read_text(encoding="utf-8")
    for phrase in ("Apache License 2.0","http.server","GB/T 7714","三线表","127.0.0.1:8787","20 MiB","AIPMAndy","metaver.vip"):
        assert phrase in readme
    assert "FastAPI + python-docx" not in readme
    assert "uvicorn goodpaper_mvp.fastapi_server" not in readme

def test_site_and_security_report_exist():
    assert (ROOT/"docs/index.html").exists()
    assert (ROOT/"SECURITY.md").exists()
    assert (ROOT/"audit/REDTEAM-2026-10-22.md").exists()
    site=(ROOT/"goodpaper_mvp/static/index.html").read_text(encoding="utf-8")
    assert 'id="copy-wechat"' in site
    assert 'id="check-btn"' in site
    assert 'id="format-btn"' in site
    assert 'id="check-format-btn"' in site
    assert 'id="batch-btn"' in site
