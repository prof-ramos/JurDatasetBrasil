# Configuração de Pre-commit Hooks

Este documento explica como configurar e usar os pre-commit hooks do JurDatasetBrasil.

## O que são Pre-commit Hooks?

Pre-commit hooks são scripts que rodam automaticamente antes de cada commit, garantindo:
- ✅ Formatação consistente de código
- ✅ Detecção de problemas de qualidade
- ✅ Verificação de segurança
- ✅ Prevenção de commits com erros

## Instalação

### 1. Instalar o pre-commit

```bash
pip install pre-commit
```

Ou adicione ao seu ambiente virtual:

```bash
pip install -r requirements-dev.txt
```

### 2. Ativar os hooks

No diretório raiz do projeto:

```bash
pre-commit install
```

## Uso

### Execução Automática

Após a instalação, os hooks rodarão automaticamente em cada `git commit`.

Se algum hook falhar:
1. Revise as mudanças sugeridas
2. Adicione os arquivos corrigidos: `git add .`
3. Tente o commit novamente

### Execução Manual

Para rodar os hooks em todos os arquivos:

```bash
pre-commit run --all-files
```

Para rodar em arquivos específicos:

```bash
pre-commit run --files scripts/config.py
```

### Pular Hooks (use com cautela!)

Em casos excepcionais, você pode pular os hooks:

```bash
git commit --no-verify -m "mensagem"
```

⚠️ **Atenção:** Isso deve ser evitado! Só use quando absolutamente necessário.

## Hooks Configurados

### 1. **Black** - Formatador de código
- Formata automaticamente código Python
- Linha máxima: 100 caracteres

### 2. **isort** - Organizador de imports
- Ordena imports alfabeticamente
- Compatível com Black

### 3. **flake8** - Linter
- Verifica erros de sintaxe e estilo
- Complexidade ciclomática
- Conformidade PEP 8

### 4. **mypy** - Type checking
- Verifica tipos estáticos
- Detecta erros de tipo

### 5. **bandit** - Segurança
- Detecta vulnerabilidades de segurança
- Verifica uso inseguro de funções

### 6. **Hooks Gerais**
- Remove espaços em branco
- Verifica sintaxe YAML/JSON
- Detecta chaves privadas
- Verifica conflitos de merge

### 7. **markdownlint** - Markdown
- Formata arquivos .md
- Garante consistência

### 8. **shellcheck** - Shell scripts
- Verifica scripts bash/sh
- Detecta erros comuns

## Atualização dos Hooks

Para atualizar para as versões mais recentes:

```bash
pre-commit autoupdate
```

## Desinstalação

Para remover os hooks:

```bash
pre-commit uninstall
```

## Troubleshooting

### Erro: "command not found: pre-commit"

Certifique-se de que o pre-commit está instalado:

```bash
pip install pre-commit
```

### Hooks muito lentos?

Use o cache do pre-commit:

```bash
pre-commit run --all-files --show-diff-on-failure
```

### Conflito com formatação existente?

Rode primeiro em todo o projeto:

```bash
pre-commit run --all-files
git add .
git commit -m "chore: aplicar formatação pre-commit"
```

## Configuração Personalizada

Edite `.pre-commit-config.yaml` para:
- Adicionar novos hooks
- Modificar argumentos
- Excluir arquivos/diretórios

Exemplo:

```yaml
- repo: https://github.com/psf/black
  rev: 24.10.0
  hooks:
    - id: black
      args: [--line-length=120]  # Modificado
```

## Integração com CI/CD

Os mesmos hooks rodam no CI/CD (GitHub Actions):

```yaml
- name: Run pre-commit
  run: |
    pip install pre-commit
    pre-commit run --all-files
```

## Recursos Adicionais

- [Documentação oficial do pre-commit](https://pre-commit.com/)
- [Lista de hooks disponíveis](https://pre-commit.com/hooks.html)
- [Black documentation](https://black.readthedocs.io/)
- [flake8 documentation](https://flake8.pycqa.org/)

## Suporte

Problemas com os hooks? Abra uma issue no GitHub:
https://github.com/prof-ramos/JurDatasetBrasil/issues
