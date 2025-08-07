# Sistema de Gerenciamento de Pedidos / Order Management System


### Descrição

Sistema básico de gerenciamento de pedidos desenvolvido em Python. O sistema utiliza arquivos Excel para persistência de dados e implementa controle de concorrência para garantir a integridade das operações.

### Funcionalidades Principais

1. **Listar Estoque**: Visualizar produtos disponíveis com quantidade em estoque
2. **Fazer Pedidos**: Realizar pedidos com validações de estoque e produto
3. **Ver Histórico**: Consultar histórico completo ou apenas pedidos ativos

### Requisitos Técnicos Atendidos

- Não permite pedidos de produtos inexistentes
- Não permite pedidos com quantidades maiores que o estoque disponível
- Garantia de atomicidade em operações concorrentes (thread-safe)
- Pedidos contêm descrição, quantidade e preço unitário
- Histórico completo de pedidos mantido
- Listagem de pedidos ativos separada


### Estrutura do Excel

O sistema utiliza um único arquivo Excel com duas abas:

**Aba "Produtos":**
- `id_produto`: ID único do produto
- `nome`: Nome do produto
- `descricao`: Descrição detalhada
- `preco_unitario`: Preço por unidade
- `quantidade_estoque`: Quantidade disponível

**Aba "Historico":**
- `id_pedido`: ID único do pedido
- `id_produto`: ID do produto pedido
- `nome_produto`: Nome do produto
- `descricao_pedido`: Descrição do pedido
- `quantidade_pedida`: Quantidade solicitada
- `preco_unitario`: Preço unitário na data do pedido
- `valor_total`: Valor total do pedido
- `data_pedido`: Data e hora do pedido
- `status`: Status do pedido (ativo/cancelado)


### Funcionalidades do Menu

1. **Listar estoque disponível**: Mostra produtos com estoque > 0
2. **Fazer pedido**: Criar novo pedido com validações
3. **Ver histórico de pedidos**: Histórico completo ou apenas ativos
4. **Cancelar pedido**: Cancelar pedido e restaurar estoque
5. **Adicionar produto**: Cadastrar novos produtos 
6. **Ver estatísticas**: Relatório geral do sistema

### Testes Implementados

- Testes unitários cobrindo todas as funcionalidades
- Testes de concorrência com múltiplas threads simultâneas
- Testes de stress com centenas de operações
- Validação de integridade dos dados
- Testes de casos extremos e tratamento de erros

### Controle de Concorrência

O sistema implementa `threading.Lock` para garantir que operações simultâneas não corrompam os dados, especialmente em cenários de:
- Múltiplos pedidos do mesmo produto
- Atualizações de estoque simultâneas
- Cancelamentos concorrentes
