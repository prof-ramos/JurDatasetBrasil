# Configuração de Variáveis de Ambiente - Vercel

## Variáveis Necessárias

Configure estas variáveis no painel da Vercel (Settings → Environment Variables):

### Produção (Production)
```
ALLOWED_ORIGINS=https://seu-dominio.com
```

### Preview/Development
```
ALLOWED_ORIGINS=*
```

## Como Configurar

1. Acesse: https://vercel.com/[seu-usuario]/jur-dataset-brasil/settings/environment-variables

2. Adicione cada variável:
   - **Key**: Nome da variável (ex: ALLOWED_ORIGINS)
   - **Value**: Valor da variável
   - **Environments**: Selecione Production, Preview e/ou Development

3. Clique em "Save"

## Variáveis Opcionais (Futuro)

Caso expanda a API para incluir features de database:

```
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-anon-key-aqui
OPENROUTER_API_KEY=sua-chave-openrouter-aqui
```

**IMPORTANTE**: Nunca commite arquivos .env com credenciais reais!
