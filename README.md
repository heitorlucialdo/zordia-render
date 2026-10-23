# ZordIA Render

Serviço que transforma JSON de slides em imagens PNG 1080x1350 (formato Instagram), no template visual da ZordIA.

## Endpoint

`POST /render`
Header: `Authorization: Bearer <TOKEN>` (se TOKEN estiver setado)
Body:
```json
{ "slides": [ { "layout": "cover", "page": "1/6", "title": "...", "sub": "..." } ] }
```
Resposta: `{ "images": ["<base64 png>", ...] }`

Layouts: cover, lista, stats, donut, pergunta, cta, impacto, destaque.

## Deploy (EasyPanel)
App a partir deste repositório GitHub. Build method: Dockerfile. Porta: 8000.
Variável de ambiente: `TOKEN` = uma senha sua.
