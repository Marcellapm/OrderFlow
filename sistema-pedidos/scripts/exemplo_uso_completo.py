from main import SistemaPedidos
import time

def demonstracao_completa():
    """Demonstração completa de todas as funcionalidades"""
    print("🎯 DEMONSTRAÇÃO COMPLETA DO SISTEMA")
    print("="*50)
    
    sistema = SistemaPedidos('dados_demo')
    
    print("\n1️⃣ ADICIONANDO PRODUTOS AO SISTEMA")
    print("-" * 30)
    
    produtos_demo = [
        ("Notebook Dell Inspiron", 2500.00, "Eletrônicos", 8),
        ("Mouse Logitech MX", 189.90, "Periféricos", 25),
        ("Teclado Mecânico RGB", 299.99, "Periféricos", 15),
        ("Monitor 27\" 4K", 1299.00, "Eletrônicos", 6),
        ("Webcam Full HD", 199.90, "Periféricos", 12),
        ("SSD 1TB Samsung", 449.90, "Armazenamento", 20)
    ]
    
    for nome, preco, categoria, estoque in produtos_demo:
        sucesso, msg = sistema.adicionar_produto(nome, preco, categoria, estoque)
        print(f"{'✅' if sucesso else '❌'} {msg}")
    
    print("\n2️⃣ LISTANDO PRODUTOS DISPONÍVEIS")
    print("-" * 30)
    sistema.listar_produtos_disponiveis()
    
    print("\n3️⃣ CRIANDO PEDIDOS VÁLIDOS")
    print("-" * 30)
    
    pedidos_teste = [
        (1, 2, "Notebooks para equipe de desenvolvimento"),
        (2, 5, "Mouses para escritório"),
        (3, 3, "Teclados para programadores"),
        (5, 2, "Webcams para reuniões remotas")
    ]
    
    for produto_id, quantidade, descricao in pedidos_teste:
        sucesso, msg = sistema.criar_pedido(produto_id, quantidade, descricao)
        print(f"{'✅' if sucesso else '❌'} {msg}")
        time.sleep(0.1)  # Pequena pausa para timestamps diferentes
    
    print("\n4️⃣ TENTANDO PEDIDOS INVÁLIDOS")
    print("-" * 30)
    
    # Produto inexistente
    sucesso, msg = sistema.criar_pedido(999, 1, "Produto que não existe")
    print(f"❌ {msg}")
    
    # Quantidade maior que estoque
    sucesso, msg = sistema.criar_pedido(4, 10, "Muitos monitores")
    print(f"❌ {msg}")
    
    # Quantidade zero
    sucesso, msg = sistema.criar_pedido(1, 0, "Quantidade inválida")
    print(f"❌ {msg}")
    
    print("\n5️⃣ LISTANDO PEDIDOS ATIVOS")
    print("-" * 30)
    sistema.listar_pedidos_ativos()
    
    print("\n6️⃣ ATUALIZANDO ESTOQUE")
    print("-" * 30)
    sucesso, msg = sistema.atualizar_estoque(4, 15)  # Aumentar estoque de monitores
    print(f"✅ {msg}")
    
    sucesso, msg = sistema.atualizar_estoque(6, 30)  # Aumentar estoque de SSDs
    print(f"✅ {msg}")
    
    print("\n7️⃣ CRIANDO MAIS PEDIDOS APÓS ATUALIZAÇÃO")
    print("-" * 30)
    sucesso, msg = sistema.criar_pedido(4, 3, "Monitores após reposição")
    print(f"✅ {msg}")
    
    sucesso, msg = sistema.criar_pedido(6, 5, "SSDs para upgrade")
    print(f"✅ {msg}")
    
    print("\n8️⃣ CANCELANDO ALGUNS PEDIDOS")
    print("-" * 30)
    
    # Cancelar pedido #2
    sucesso, msg = sistema.cancelar_pedido(2)
    print(f"✅ {msg}")
    
    # Tentar cancelar pedido inexistente
    sucesso, msg = sistema.cancelar_pedido(999)
    print(f"❌ {msg}")
    
    # Tentar cancelar pedido já cancelado
    sucesso, msg = sistema.cancelar_pedido(2)
    print(f"❌ {msg}")
    
    print("\n9️⃣ VERIFICANDO PEDIDOS ATIVOS APÓS CANCELAMENTOS")
    print("-" * 30)
    sistema.listar_pedidos_ativos()
    
    print("\n🔟 HISTÓRICO COMPLETO DE PEDIDOS")
    print("-" * 30)
    sistema.historico_completo()
    
    print("\n📊 ESTATÍSTICAS FINAIS DO SISTEMA")
    print("-" * 30)
    stats = sistema.obter_estatisticas()
    
    print(f"📦 Total de produtos cadastrados: {stats['total_produtos']}")
    print(f"📈 Produtos com estoque disponível: {stats['produtos_com_estoque']}")
    print(f"📋 Total de pedidos realizados: {stats['total_pedidos']}")
    print(f"✅ Pedidos ativos: {stats['pedidos_ativos']}")
    print(f"❌ Pedidos cancelados: {stats['pedidos_cancelados']}")
    print(f"💰 Valor total dos pedidos ativos: R$ {stats['valor_total_pedidos_ativos']:.2f}")
    
    print("\n🎯 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*50)
    
    return sistema

if __name__ == "__main__":
    demonstracao_completa()
