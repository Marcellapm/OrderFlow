from main import SistemaPedidos

def exemplo_uso_completo():
    """Demonstração completa das 3 funcionalidades principais"""
    print("DEMONSTRAÇÃO DO SISTEMA DE PEDIDOS")
    print("="*50)
    
    sistema = SistemaPedidos('dados/exemplo.xlsx')
    
    print("\nPREPARANDO SISTEMA COM PRODUTOS INICIAIS")
    print("-" * 40)
    
    # Adicionar produtos de exemplo
    produtos_exemplo = [
        ("Notebook Dell Inspiron", "Notebook para trabalho e estudos", 2500.00, 8),
        ("Mouse Logitech MX", "Mouse ergonômico sem fio", 189.90, 25),
        ("Teclado Mecânico RGB", "Teclado gamer com iluminação", 299.99, 15),
        ("Monitor 27\" 4K", "Monitor profissional ultra HD", 1299.00, 6),
        ("Webcam Full HD", "Webcam para videoconferências", 199.90, 12),
        ("SSD 1TB Samsung", "Armazenamento rápido e confiável", 449.90, 20),
        ("Headset Gamer", "Fone com microfone para jogos", 159.90, 0)  # Sem estoque
    ]
    
    for nome, desc, preco, estoque in produtos_exemplo:
        sucesso, msg = sistema.adicionar_produto(nome, desc, preco, estoque)
        print(f"{'[OK]' if sucesso else '[ERRO]'} {msg}")
    
    print("\n" + "="*60)
    print("DEMONSTRAÇÃO DAS 3 FUNCIONALIDADES PRINCIPAIS")
    print("="*60)
    
    # 1. LISTAR ESTOQUE
    print("\n1. FUNCIONALIDADE: LISTAR ESTOQUE")
    print("="*40)
    sistema.listar_estoque()
    
    # 2. FAZER PEDIDOS
    print("\n2. FUNCIONALIDADE: FAZER PEDIDOS")
    print("="*40)
    
    pedidos_exemplo = [
        (1, 2, "Notebooks para equipe de desenvolvimento"),
        (2, 5, "Mouses para escritório"),
        (3, 3, "Teclados para programadores"),
        (5, 2, "Webcams para reuniões remotas"),
        (6, 4, "SSDs para upgrade dos computadores")
    ]
    
    print("Criando pedidos de exemplo...")
    for produto_id, quantidade, descricao in pedidos_exemplo:
        sucesso, msg = sistema.fazer_pedido(produto_id, quantidade, descricao)
        print(f"\n{msg}")
    
    print("\nTestando pedidos que devem falhar...")
    
    # Produto inexistente
    sucesso, msg = sistema.fazer_pedido(999, 1, "Produto que não existe")
    print(f"\n[ERRO ESPERADO] {msg}")
    
    # Quantidade maior que estoque
    sucesso, msg = sistema.fazer_pedido(4, 10, "Muitos monitores")
    print(f"\n[ERRO ESPERADO] {msg}")
    
    # Produto sem estoque
    sucesso, msg = sistema.fazer_pedido(7, 1, "Headset sem estoque")
    print(f"\n[ERRO ESPERADO] {msg}")
    
    # 3. VER HISTÓRICO
    print("\n3. FUNCIONALIDADE: VER HISTÓRICO")
    print("="*40)
    
    print("\nHistórico de pedidos ativos:")
    sistema.ver_historico(apenas_ativos=True)
    
    print("\nHistórico completo:")
    sistema.ver_historico(apenas_ativos=False)
    
    # FUNCIONALIDADE EXTRA: CANCELAR PEDIDO
    print("\nFUNCIONALIDADE EXTRA: CANCELAR PEDIDO")
    print("="*40)
    
    print("Cancelando pedido #2...")
    sucesso, msg = sistema.cancelar_pedido(2)
    print(f"\n{msg}")
    
    print("\nHistórico após cancelamento:")
    sistema.ver_historico(apenas_ativos=False)
    
    # VERIFICAR ESTOQUE APÓS OPERAÇÕES
    print("\nESTOQUE APÓS TODAS AS OPERAÇÕES:")
    print("="*40)
    sistema.listar_estoque()
    
    # ESTATÍSTICAS FINAIS
    print("\nESTATÍSTICAS FINAIS DO SISTEMA:")
    print("="*40)
    stats = sistema.obter_estatisticas()
    
    print(f"Total de produtos: {stats['total_produtos']}")
    print(f"Produtos em estoque: {stats['produtos_em_estoque']}")
    print(f"Produtos sem estoque: {stats['produtos_sem_estoque']}")
    print(f"Total de pedidos: {stats['total_pedidos']}")
    print(f"Pedidos ativos: {stats['pedidos_ativos']}")
    print(f"Pedidos cancelados: {stats['pedidos_cancelados']}")
    print(f"Valor pedidos ativos: R$ {stats['valor_total_pedidos_ativos']:.2f}")
    print(f"Valor total geral: R$ {stats['valor_total_geral']:.2f}")
    
    print("\nDEMONSTRAÇÃO CONCLUÍDA!")
    print("="*50)
    print("Sistema funcionando com:")
    print("   - Controle de estoque em tempo real")
    print("   - Validações robustas")
    print("   - Operações atômicas (thread-safe)")
    print("   - Histórico completo de transações")
    print("   - Dados persistidos em Excel")

if __name__ == "__main__":
    exemplo_uso_completo()
