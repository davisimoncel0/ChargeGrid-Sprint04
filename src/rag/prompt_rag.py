from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def load_prompt(version="v2"):
    if version not in ("v1", "v2"):
        raise ValueError("Versao invalida")
    return (ROOT / "prompts" / f"rag_{version}.md").read_text(encoding="utf-8")
