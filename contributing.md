# Contributing to Otakuverse

Obrigado por querer contribuir com o projeto! Este documento explica
como configurar o ambiente, clonar o repositório e fazer alterações.

------------------------------------------------------------------------

## Como clonar o repositório

Execute:

``` bash
git clone https://github.com/Nobutann/OtakuVerse.git
cd otakuverse
```

Agora você pode alterar o código.

------------------------------------------------------------------------

## Configuração do Ambiente Python

### Criar e ativar o ambiente virtual

``` bash
python -m venv venv
# Para Windows:
venv\Scripts\activate
# Para Linux/Mac:
source venv/bin/activate
```

### Instalar dependências

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

## Cada alteração deve ser feita no módulo correspondente:

-   **animes** -- funcionalidades relacionadas a animes\
-   **lists** -- listas, coleções, favoritos\
-   **users** -- autenticação, perfis\
-   **templates** -- HTML\
-   **static** -- CSS, JS, imagens\
-   **core** -- configurações do projeto

------------------------------------------------------------------------

## Como contribuir

### 1. Crie uma nova branch

``` bash
git checkout -b feature/minha-feature
```

### 2. Faça alterações no código

Organize tudo na pasta apropriada.

### 3. Commit claro

    feat: adicionar novo layout para página de animes
    fix: corrigir erro no login
    docs: atualizar documentação

### 4. Envie a branch

``` bash
git push origin feature/minha-feature
```

### 5. Abra um Pull Request

Explique o que foi alterado e por quê.

------------------------------------------------------------------------

## 🧪 Testes

Testes E2E ficam em:

    /cypress/e2e/

Execute antes de abrir o PR, caso esteja alterando comportamento:

``` bash
npx cypress open
```

------------------------------------------------------------------------

## 🗨️ Dúvidas?

Abra uma issue no repositório. Obrigado por contribuir! 🎉
