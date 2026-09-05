# Newsletter — Kit

A newsletter é uma projeção do Second Brain. O site continua sendo a publicação canônica; o e-mail apenas anuncia um novo essay e aponta para ele.

## Publicar

No front matter de um essay público:

```yaml
visibility: public
newsletter: true
```

Opcionalmente:

```yaml
newsletter_issue: 1
newsletter_subject: "Novo essay — Título"
newsletter_summary: "Resumo específico para o e-mail."
newsletter_preview: "Texto curto exibido pelo cliente de e-mail."
```

`newsletter_issue` evita reenvio acidental quando o essay é editado. O padrão é `1`. Só aumente para `2`, `3`, etc. se quiser deliberadamente anunciar uma nova edição do mesmo essay.

Não há comando extra de publicação: `seal_publication.py` gera automaticamente `site/.github/newsletter-manifest.json`. O manifesto contém apenas metadados públicos e nunca entra no artefato do GitHub Pages.

## E-mail

Padrão gerado automaticamente:

- Assunto: `Novo essay — <título>`
- Preheader: resumo truncado do essay
- Cabeçalho: `Second Brain`
- Título do essay
- Resumo
- Tempo estimado de leitura
- CTA: `Ler o essay completo →`
- Assinatura: `Gustavo Zambrano · Second Brain`

O corpo completo permanece no site. O broadcast é privado no Kit (`public: false`) para não criar uma segunda versão pública do artigo.

## GitHub → Kit

O workflow `.github/workflows/newsletter.yml` do `second-brain-site` só roda depois de um deploy Pages bem-sucedido em `main`.

Configuração no repositório do site:

- Secret `KIT_API_KEY` — API key v4 do Kit.
- Variable `KIT_NEWSLETTER_ENABLED` — `true` habilita envio; qualquer outro valor mantém dry-run.
- Variable `SITE_BASE_URL` — opcional; padrão `https://gitzambrano.github.io/second-brain-site`.
- Variable `KIT_EMAIL_TEMPLATE_ID` — opcional; usa o template padrão da conta quando ausente.

Proteções:

- primeiro deploy cria baseline e não envia nada;
- rerun não duplica broadcast;
- edição comum do essay não reenvia;
- envio real exige `KIT_NEWSLETTER_ENABLED=true` e `KIT_API_KEY`;
- o broadcast só é criado depois de o Pages terminar com sucesso.

## Formulário de assinatura

No Kit, crie um **Form → Inline**, mantenha double opt-in e use o embed JavaScript recomendado pelo Kit. O UID/embed é público; a API key nunca vai para HTML ou JavaScript do site.

Esta é a única parte que depende da conta Kit: o Form precisa existir para termos o UID/embed real. Depois disso, o embed deve ser colocado no template público do Atlas e validado em desktop/mobile antes do merge.
