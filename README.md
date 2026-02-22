# SUAP Scraper API

## Introdução

API robusta para extração de dados do Sistema Unificado de Administração Pública (SUAP) do IFSP, criando uma ponte entre o sistema oficial acadêmico e seus serviços. Desenvolvida utilizando **FastAPI** para endpoints assíncronos e **Playwright** para renderização e web scraping headless nas páginas do sistema.

**Endereço Base:** `http://localhost:8000` (Padrão local)

## Autenticação

Esta API atua como um wrapper direto do SUAP. Todas as chamadas para os recursos principais exigem que o cliente envie usuário e senha em texto plano, que serão autenticados via Playwright direto no suap.

**Formato padrão no Body:**
```json
{
  "usuario": "seu_prontuario",
  "senha": "sua_senha_do_suap"
}
```

> **Aviso de Segurança:** Como a API exige as senhas dos alunos diretamente a cada requisição, as chamadas com destino a esta API deverão ocorrer exclusivamente sobre HTTPS/TLS (quando em produção) ou por trás de um túnel fechado.

## Quick Start

1. **Clone e Instale:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn playwright pydantic requests
playwright install chromium
```

2. **Execute o Servidor:**
```bash
./run.sh
# Ou: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Endpoints

### 1. Sistema e Saúde (Healthcheck)

Verificação fácil se a API está online e pronta para aceitar requests.

**Endpoint:** `GET /health`

**Success Response (200 OK):**
```json
{
  "status": "ativo"
}
```

---

### 2. Validar Login

Tenta submeter as informações do usuário ao SUAP, e responde rápido em caso de aprovação.

**Endpoint:** `POST /validar-login`
**Authentication:** Prontuário e Senha requeridos no Body.

**Request Body:**
```json
{
  "usuario": "123456",
  "senha": "MySecretPassword"
}
```

**Success Response (200 OK):**
```json
{
  "sucesso": true,
  "mensagem": "Login realizado com sucesso"
}
```

**Error Response**
```json
{
  "sucesso": false,
  "mensagem": "Falha no login ou credenciais inválidas"
}
```

---

### 3. Obter Perfil

Busca os dados descritivos, dados curriculares básicos e imagem de perfil do aluno logado.

**Endpoint:** `POST /perfil`
**Authentication:** Prontuário e Senha requeridos.

**Success Response (200 OK):**
```json
{
  "sucesso": true,
  "perfil": {
    "nome_completo": "João da Silva",
    "periodo_referencia": "3º",
    "ira": "8,5",
    "url_perfil": "https://suap.ifsp.edu.br/..."
  }
}
```

---

### 4. Obter Boletim (Retorno Extensão CSV)

Busca notas formatadas nos blocos 1, 2, 3 e 4. Diferente dos JSON padrões, este endpoint cospe uma tabela delimitada (CSV) direta.

**Endpoint:** `POST /boletim`
**Authentication:** Prontuário e Senha requeridos.

**Success Response (200 OK | Content-Type: text/csv):**
```csv
Área de Conhecimento,Disciplina,N1,N2,N3,N4,MFD
3 - Ciências da Natureza,BIOLOGIA,-,80,-,90,85
1 - Informática,PROGRAMAÇÃO,90,100,-,-,95
```

---

### 5. Listar Disciplinas Disponíveis

Recomenda-se chamar este endpoint primariamente se deseja acionar recursos avançados depois (como ver os Critérios das Disciplinas). Extrairá exatamente os Strings identificadores da tabela.

**Endpoint:** `POST /disciplinas`
**Authentication:** Prontuário e Senha requeridos.

**Success Response (200 OK):**
```json
{
  "sucesso": true,
  "disciplinas": [
    "INT.08771 (BRAART2) - ARTE 2",
    "INT.08776 (BRABIO3) - BIOLOGIA 3"
  ]
}
```

---

### 6. Critérios de Avaliação

Busca como o professor informou que comporá a nota deste aluno naquela disciplina (ex: "Prova: 50 | Trabalho: 50").

**Endpoint:** `POST /criterios-avaliacao`
**Authentication:** Prontuário e Senha requeridos.
*Pode-se informar o nome exato da disciplina do array de "disciplinas" listado outrora, ou a string "todas".*

**Request Body:**
```json
{
  "usuario": "123456",
  "senha": "MySecretPassword",
  "disciplina": "todas"
}
```

**Success Response (200 OK):**
```json
{
  "sucesso": true,
  "dados": [
    {
      "disciplina": "INT.08771 (BRAART2) - ARTE 2",
      "criterios": "Atividade Prática: 10,0",
      "mensagem": null
    }
  ]
}
```

---

### 7. Plano de Aulas (Retorno Extensão CSV)

Exporta o cronograma planejado (Data e Conteúdo) que os professores deram check na plataforma oficial.

**Endpoint:** `POST /plano-de-aulas`
**Authentication:** Prontuário e Senha requeridos.

**Request Body:**
```json
{
  "usuario": "123456",
  "senha": "MySecretPassword",
  "disciplina": "todas"
}
```

**Success Response (200 OK | Content-Type: text/csv):**
```csv
Disciplina,Data,Conteúdo,Metodologia,Mensagem
INT.08771 (BRAART2) - ARTE 2,05/10/2026,Estudos de Pintura,Expositiva,
```

## Error Handling

Quando falhar, o serviço não usará um padrão HTTP 4xx na maioria das validações falhas do *scraper*. Em vez disso, ele responderá HTTP `200` portando flag `"sucesso": false` se a credencial logar mal.
Já casos de quebra drástica (exception server) podem retornar `500`.
A API retornará `400 Bad Request` apenas se o Playwright desmanchar tentando rodar os exports em CSV. 

| Código | Descrição |
|--------|-------------|
| **200** | Retorno padrão para sucessos ou quando o Scraper finalizou mas a senha estava errada (`sucesso: false`). |
| **400** | Exceção interceptada na transformação dos dados avançados (Boletins ou Plano Aulas CSV) |
| **500** | Erro Interno (Falha grave no Playwright ou timeout inesperado no Chromium) |

**Formato padrão de erro do Scraper:**
```json
{
  "sucesso": false,
  "mensagem": "Falha no login ou credenciais inválidas"
}
```