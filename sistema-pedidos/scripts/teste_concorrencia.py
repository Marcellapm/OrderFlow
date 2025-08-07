import threading
import time
import random
from main import SistemaPedidos

def teste_concorrencia_avancado():
    """Teste avançado de concorrência com múltiplos cenários"""
    print("TESTE AVANÇADO DE CONCORRÊNCIA")
    print("="*50)
    
    sistema = SistemaPedidos('dados_teste/concorrencia.xlsx')
    
    # Preparar dados de teste
    print("Preparando produtos para teste...")
    sistema.adicionar_produto("Produto A", "Produto com estoque limitado", 100.00, 10)
    sistema.adicionar_produto("Produto B", "Produto popular", 200.00, 5)
    sistema.adicionar_produto("Produto C", "Produto abundante", 50.00, 20)
    
    resultados_globais = {
        'pedidos_criados': 0,
        'pedidos_falharam': 0,
        'cancelamentos_ok': 0,
        'cancelamentos_falha': 0
    }
    
    # Lock para proteger acesso aos resultados globais
    lock_resultados = threading.Lock()
    
    def worker_criar_pedidos(worker_id, produto_id, max_pedidos=5):
        """Worker que cria pedidos aleatórios"""
        for i in range(max_pedidos):
            quantidade = random.randint(1, 3)
            sucesso, _ = sistema.fazer_pedido(produto_id, quantidade, f"Pedido worker {worker_id}-{i}")
            
            # Atualizar resultados de forma thread-safe
            with lock_resultados:
                if sucesso:
                    resultados_globais['pedidos_criados'] += 1
                else:
                    resultados_globais['pedidos_falharam'] += 1
            
            # Simular tempo de processamento
            time.sleep(random.uniform(0.01, 0.05))
    
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
    
    print("Iniciando teste com múltiplas threads...")
    
    # Criar threads para diferentes operações
    threads = []
    
    # 5 threads criando pedidos do produto A (estoque limitado)
    for i in range(5):
        t = threading.Thread(target=worker_criar_pedidos, args=(f"A{i}", 1, 3))
        threads.append(t)
    
    # 3 threads criando pedidos do produto B (muito limitado)
    for i in range(3):
        t = threading.Thread(target=worker_criar_pedidos, args=(f"B{i}", 2, 2))
        threads.append(t)
    
    # 4 threads criando pedidos do produto C (abundante)
    for i in range(4):
        t = threading.Thread(target=worker_criar_pedidos, args=(f"C{i}", 3, 4))
        threads.append(t)
    
    # 2 threads cancelando pedidos
    for i in range(2):
        t = threading.Thread(target=worker_cancelar_pedidos, args=(f"Cancel{i}", 8))
        threads.append(t)
    
    # Iniciar todas as threads
    inicio = time.time()
    for thread in threads:
        thread.start()
    
    # Aguardar todas terminarem
    for thread in threads:
        thread.join()
    
    fim = time.time()
    
    print(f"\nTeste concluído em {fim - inicio:.2f} segundos")
    print("\nRESULTADOS DO TESTE:")
    print(f"Pedidos criados com sucesso: {resultados_globais['pedidos_criados']}")
    print(f"Pedidos que falharam: {resultados_globais['pedidos_falharam']}")
    print(f"Cancelamentos bem-sucedidos: {resultados_globais['cancelamentos_ok']}")
    print(f"Cancelamentos que falharam: {resultados_globais['cancelamentos_falha']}")
    
    # Verificar integridade final
    print("\nVERIFICAÇÃO DE INTEGRIDADE:")
    stats = sistema.obter_estatisticas()
    print(f"Total de pedidos no sistema: {stats['total_pedidos']}")
    print(f"Pedidos ativos: {stats['pedidos_ativos']}")
    print(f"Pedidos cancelados: {stats['pedidos_cancelados']}")
    print(f"Valor total pedidos ativos: R$ {stats['valor_total_pedidos_ativos']:.2f}")
    
    # Verificar se não há inconsistências
    produtos, historico = sistema._carregar_dados()
    
    print("\nESTOQUE FINAL:")
    for _, produto in produtos.iterrows():
        qtd = int(produto['quantidade_estoque'])
        print(f"  {produto['nome']}: {qtd} unidades")
    
    # Validar que estoque não ficou negativo (crítico)
    estoques_negativos = produtos[produtos['quantidade_estoque'] < 0]
    if not estoques_negativos.empty:
        print("ERRO: Encontrados estoques negativos!")
        print(estoques_negativos)
        return False
    
    print("\nTESTE DE CONCORRÊNCIA PASSOU - SISTEMA MANTEVE INTEGRIDADE!")
    return True

if __name__ == "__main__":
    sucesso = teste_concorrencia_avancado()
    
    print("\n" + "="*60)
    print("RESULTADO FINAL DOS TESTES DE CONCORRÊNCIA")
    print("="*60)
    
    if sucesso:
        print("TODOS OS TESTES DE CONCORRÊNCIA PASSARAM!")
    else:
        print("ALGUNS TESTES FALHARAM!")
