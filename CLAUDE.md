# Second Brain

As instruções do projeto vivem em `AGENTS.md`, fonte única para todos os agentes.
Este arquivo existe apenas porque o Claude Code procura por `CLAUDE.md`, e se
limita a importá-lo. Nunca duplique conteúdo aqui: edite `AGENTS.md`.

Pelo mesmo motivo, `.claude/skills/` é um espelho gerado de `.agents/skills/`
(fonte única), mantido por `scripts/sync_skills.py` e disparado pelo hook
`SessionStart` em `.claude/settings.json`. Nunca edite nada dentro de
`.claude/skills/`.

@AGENTS.md
