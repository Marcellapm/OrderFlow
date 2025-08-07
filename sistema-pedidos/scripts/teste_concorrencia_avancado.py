import threading
import time
import random
from main import SistemaPedidos

def teste_concorrencia_completo():
    """Teste avançado de concorrência com múltiplos cenários"""
    print("🔬 TESTE AVANÇADO DE CONCORRÊNCIA")
    print("="*50)
    
    sistema = SistemaPedidos('dados_concorrencia')
    
    # Preparar dados de teste
    print("📦 Preparando produtos para teste...")
    sistema.adicionar_produto("Produto A", 100.00, "Categoria", 10)
    sistema.adicionar_produto("Produto B", 200.00, "Categoria", 5)
    sistema.adicionar_produto("Produto C", 50.00, "Categoria", 20)
    
    resultados_globais = {
        'pedidos_criados': 0,
        'pedidos_falharam': 0,
        'cancelamentos_ok': 0,
        'cancelamentos_falha': 0,
        'atualizacoes_estoque': 0
    }
    
    lock_resultados = threading.Lock()
    
    def worker_criar_pedidos(worker_id, produto_id, max_pedidos=5):
        """Worker que cria pedidos aleatórios"""
        for i in range(max_pedidos):
            quantidade = random.randint(1, 3)
            sucesso, _ = sistema.criar_pedido(produto_id, quantidade, f"Pedido worker {worker_id}-{i}")
            
            with lock_resultados:
                if sucesso:
                    resultados_globais['pedidos_criados'] += 1
                else:
                    resultados_globais['pedidos_falharam'] += 1
            
            time.sleep(random.uniform(0.01, 0.05))  # Simular tempo de processamento
    
    def worker_cancelar_pedidos(worker_id, max_tentativas=10):
        """Worker que tenta cancelar pedidos aleatórios"""
        for i in range(max_tentativas):
            id_pedido = random.randint(1, 20)  # Tentar IDs aleatórios
            sucesso, _ = sistema.cancelar_pedido(id_pedido)
            
            with lock_resultados:
                if sucesso:
                    resultados_globais['cancelamentos_ok'] += 1
                else:
                    resultados_globais['cancelamentos_falha'] += 1
            
            time.sleep(random.uniform(0.01, 0.03))
    
    def worker_atualizar_estoque(worker_id, max_atualizacoes=3):
        """Worker que atualiza estoques"""
        for i in range(max_atualizacoes):
            produto_id = random.randint(1, 3)
            nova_quantidade = random.randint(5, 15)
            sucesso, _ = sistema.atualizar_estoque(produto_id, nova_quantidade)
            
            with lock_resultados:
                if sucesso:
                    resultados_globais['atualizacoes_estoque'] += 1
            
            time.sleep(random.uniform(0.02, 0.08))
    
    print("🚀 Iniciando teste com múltiplas threads...")
    
    # Criar threads para diferentes operações
    threads = []
    
    # 5 threads criando pedidos do produto A
    for i in range(5):
        t = threading.Thread(target=worker_criar_pedidos, args=(f"A{i}", 1, 3))
        threads.append(t)
    
    # 3 threads criando pedidos do produto B
    for i in range(3):
        t = threading.Thread(target=worker_criar_pedidos, args=(f"B{i}", 2, 2))
        threads.append(t)
    
    # 4 threads criando pedidos do produto C
    for i in range(4):
        t = threading.Thread(target=worker_criar_pedidos, args=(f"C{i}", 3, 4))
        threads.append(t)
    
    # 2 threads cancelando pedidos
    for i in range(2):
        t = threading.Thread(target=worker_cancelar_pedidos, args=(f"Cancel{i}", 8))
        threads.append(t)
    
    # 2 threads atualizando estoque
    for i in range(2):
        t = threading.Thread(target=worker_atualizar_estoque, args=(f"Stock{i}", 2))
        threads.append(t)
    
    # Iniciar todas as threads
    inicio = time.time()
    for thread in threads:
        thread.start()
    
    # Aguardar todas terminarem
    for thread in threads:
        thread.join()
    
    fim = time.time()
    
    print(f"\n⏱️  Teste concluído em {fim - inicio:.2f} segundos")
    print("\n📊 RESULTADOS DO TESTE:")
    print(f"✅ Pedidos criados com sucesso: {resultados_globais['pedidos_criados']}")
    print(f"❌ Pedidos que falharam: {resultados_globais['pedidos_falharam']}")
    print(f"✅ Cancelamentos bem-sucedidos: {resultados_globais['cancelamentos_ok']}")
    print(f"❌ Cancelamentos que falharam: {resultados_globais['cancelamentos_falha']}")
    print(f"✅ Atualizações de estoque: {resultados_globais['atualizacoes_estoque']}")
    
    # Verificar integridade final
    print("\n🔍 VERIFICAÇÃO DE INTEGRIDADE:")
    stats = sistema.obter_estatisticas()
    print(f"Total de pedidos no sistema: {stats['total_pedidos']}")
    print(f"Pedidos ativos: {stats['pedidos_ativos']}")
    print(f"Pedidos cancelados: {stats['pedidos_cancelados']}")
    print(f"Valor total pedidos ativos: R$ {stats['valor_total_pedidos_ativos']:.2f}")
    
    # Verificar se não há inconsistências
    produtos, estoque, pedidos = sistema._carregar_dados()
    
    print("\n📦 ESTOQUE FINAL:")
    for _, produto in produtos.iterrows():
        estoque_produto = estoque[estoque['id_produto'] == produto['id_produto']]
        if not estoque_produto.empty:
            qtd = int(estoque_produto.iloc[0]['quantidade_disponivel'])
            print(f"  {produto['nome']}: {qtd} unidades")
    
    # Validar que estoque não ficou negativo
    estoques_negativos = estoque[estoque['quantidade_disponivel'] < 0]
    if not estoques_negativos.empty:
        print("🚨 ERRO: Encontrados estoques negativos!")
        print(estoques_negativos)
        return False
    
    print("\n✅ TESTE DE CONCORRÊNCIA PASSOU - SISTEMA MANTEVE INTEGRIDADE!")
    return True

def teste_stress_sistema():
    """Teste de stress com muitas operações simultâneas"""
    print("\n💪 TESTE DE STRESS DO SISTEMA")
    print("="*40)
    
    sistema = SistemaPedidos('dados_stress')
    
    # Preparar muitos produtos
    print("📦 Criando 50 produtos...")
    for i in range(1, 51):
        sistema.adicionar_produto(f"Produto {i}", random.uniform(10, 1000), f"Categoria {i%5}", random.randint(10, 100))
    
    def operacao_aleatoria(worker_id, num_operacoes=100):
        """Executa operações aleatórias no sistema"""
        for _ in range(num_operacoes):
            operacao = random.choice(['criar_pedido', 'cancelar_pedido', 'atualizar_estoque'])
            
            try:
                if operacao == 'criar_pedido':
                    produto_id = random.randint(1, 50)
                    quantidade = random.randint(1, 5)
                    sistema.criar_pedido(produto_id, quantidade)
                
                elif operacao == 'cancelar_pedido':
                    pedido_id = random.randint(1, 200)
                    sistema.cancelar_pedido(pedido_id)
                
                elif operacao == 'atualizar_estoque':
                    produto_id = random.randint(1, 50)
                    nova_quantidade = random.randint(0, 50)
                    sistema.atualizar_estoque(produto_id, nova_quantidade)
                
            except Exception as e:
                print(f"Worker {worker_id} encontrou erro: {e}")
            
            # Pequena pausa para não sobrecarregar
            time.sleep(random.uniform(0.001, 0.01))
    
    print("🚀 Iniciando teste de stress com 20 workers...")
    
    threads = []
    inicio = time.time()
    
    # Criar 20 workers fazendo 100 operações cada
    for i in range(20):
        t = threading.Thread(target=operacao_aleatoria, args=(i, 100))
        threads.append(t)
        t.start()
    
    # Aguardar todos terminarem
    for thread in threads:
        thread.join()
    
    fim = time.time()
    
    print(f"\n⏱️  Teste de stress concluído em {fim - inicio:.2f} segundos")
    
    # Verificar integridade final
    stats = sistema.obter_estatisticas()
    print(f"\n📊 ESTATÍSTICAS FINAIS:")
    print(f"Total de produtos: {stats['total_produtos']}")
    print(f"Total de pedidos: {stats['total_pedidos']}")
    print(f"Pedidos ativos: {stats['pedidos_ativos']}")
    print(f"Valor total: R$ {stats['valor_total_pedidos_ativos']:.2f}")
    
    # Verificar integridade dos dados
    _, estoque, _ = sistema._carregar_dados()
    estoques_negativos = estoque[estoque['quantidade_disponivel'] < 0]
    
    if not estoques_negativos.empty:
        print("🚨 FALHA: Sistema permitiu estoques negativos!")
        return False
    
    print("✅ TESTE DE STRESS PASSOU - SISTEMA MANTEVE INTEGRIDADE!")
    return True

if __name__ == "__main__":
    sucesso1 = teste_concorrencia_completo()
    sucesso2 = teste_stress_sistema()
    
    print("\n" + "="*60)
    print("🏁 RESULTADO FINAL DOS TESTES DE CONCORRÊNCIA")
    print("="*60)
    
    if sucesso1 and sucesso2:
        print("TODOS OS TESTES DE CONCORRÊNCIA PASSARAM!")
    else:
        print("ALGUNS TESTES FALHARAM!")
