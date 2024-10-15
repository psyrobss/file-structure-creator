# File Structure Creator

![GitHub license](https://img.shields.io/github/license/psyrobss/file-structure-creator.svg)

## Descrição

O **File Structure Creator** é um aplicativo de interface gráfica desenvolvido em Python com PyQt5, que permite aos usuários criar estruturas de diretórios e arquivos a partir de uma entrada de texto formatada. Ideal para desenvolvedores que desejam configurar rapidamente a estrutura de seus projetos.

## Funcionalidades

- **Seleção de Diretório de Destino:** Escolha onde a estrutura será criada.
- **Validação em Tempo Real:** Verifica a consistência da estrutura inserida.
- **Criação Automática:** Gera diretórios e arquivos conforme especificado.
- **Tratamento de Nomes Duplicados:** Adiciona sufixos numéricos (`01`, `02`, etc.) para evitar duplicatas.

## Como Usar

1. **Selecionar Diretório de Destino:**
   - Clique no botão "Selecionar Diretório de Destino" e escolha o local onde deseja criar a estrutura.

2. **Inserir Estrutura:**
   - No editor de texto, cole a estrutura desejada. Exemplo:
     ```
     Pasta/
     ├── Pasta/
     │   ├── Pasta/
     │   │   ├── Arquivo.js
     │   │   ├── Arquivo.js
     │   │   └── Arquivo.js
     │   ├── Pasta/
     │   │   ├── Arquivo.js
     │   │   ├── Arquivo.js
     │   │   ├── Arquivo.js
     │   │   └── Arquivo.js
     │   ├── Pasta/
     │   │   ├── Arquivo.js
     │   │   └── Arquivo.js
     │   ├── Pasta/
     │   │   └── Arquivo.js
     │   └── Arquivo.js
     ├── Pasta/
     ```

3. **Validar Estrutura:**
   - A aplicação validará automaticamente a estrutura. Se houver erros, mensagens serão exibidas abaixo do editor.

4. **Criar Estrutura:**
   - Após a validação bem-sucedida, clique em "Criar Estrutura de Arquivos" para gerar os diretórios e arquivos.

## Contribuição

Este projeto foi desenvolvido com a ajuda do ChatGPT, que forneceu orientação na criação e depuração do aplicativo.

Se você deseja contribuir, sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
