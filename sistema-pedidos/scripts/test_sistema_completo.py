import unittest
import pandas as pd
import os
import shutil
import threading
import time
from main import SistemaPedidos

class TestSistemaPedidos(unittest.TestCase):
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.arquivo_teste = 'dados_teste/sistema_teste.xlsx'
        self.sistema = SistemaPedidos(self.arquivo_teste)
        
        # Limpar dados de teste anteriores
        pasta_teste = os.path.dirname(self.arquivo_teste)
        if os.path.exists(pasta_teste):
            shutil.rmtree(pasta_teste)
        
        # Recriar sistema limpo
        self.sistema = SistemaPedidos(self.arquivo_teste)
    
    def tearDown(self):
        """Limpeza após cada teste"""
        pasta_teste = os.path.dirname(self.arquivo_teste)
        if os.path.exists(pasta_teste):
            shutil.rmtree(pasta_teste)
    
    def test_inicializacao_arquivo_excel(self):
        """Testa se o arquivo Excel é criado corretamente"""
        self.assertTrue(os.path.exists(self.arquivo_teste))
        
        # Verificar se arquivo tem duas abas
        produtos, historico = self.sistema._carregar_dados()
        self.assertTrue(produtos.empty)
        self.assertTrue(historico.empty)
        
        # Verificar colunas corretas
        self.assertListEqual(list(produtos.columns), 
                           ['id_produto', 'nome', 'descricao', 'preco_unitario', 'quantidade_estoque'])
        self.assertListEqual(list(historico.columns), 
                           ['id_pedido', 'id_produto', 'nome_produto', 'descricao_pedido', 
                            'quantidade_pedida', 'preco_unitario', 'valor_total', 'data_pedido', 'status'])
    
    def test_adicionar_produto_sucesso(self):
        """Testa adição de produto com sucesso"""
        sucesso, mensagem = self.sistema.adicionar_produto(
            "Notebook Dell", "Notebook para desenvolvimento", 2500.00, 10
        )
        
        self.assertTrue(sucesso)
        self.assertIn("Notebook Dell", mensagem)
        self.assertIn("ID: 1", mensagem)
        
        # Verificar se produto foi salvo
        produtos, _ = self.sistema._carregar_dados()
        self.assertEqual(len(produtos), 1)
        self.assertEqual(produtos.iloc[0]['nome'], "Notebook Dell")
        self.assertEqual(produtos.iloc[0]['descricao'], "Notebook para desenvolvimento")
        self.assertEqual(produtos.iloc[0]['preco_unitario'], 2500.00)
        self.assertEqual(produtos.iloc[0]['quantidade_estoque'], 10)
    
    def test_adicionar_produto_validacoes(self):
        """Testa validações na adição de produtos"""
        # Nome vazio
        sucesso, mensagem = self.sistema.adicionar_produto("", "Desc", 100.00, 5)
        self.assertFalse(sucesso)
        self.assertIn("Nome do produto não pode estar vazio", mensagem)
        
        # Preço inválido
        sucesso, mensagem = self.sistema.adicionar_produto("Produto", "Desc", 0, 5)
        self.assertFalse(sucesso)
        self.assertIn("Preço deve ser maior que zero", mensagem)
        
        # Quantidade negativa
        sucesso, mensagem = self.sistema.adicionar_produto("Produto", "Desc", 100.00, -5)
        self.assertFalse(sucesso)
        self.assertIn("Quantidade em estoque não pode ser negativa", mensagem)
        
        # Produto duplicado
        self.sistema.adicionar_produto("Produto Teste", "Desc", 100.00, 5)
        sucesso, mensagem = self.sistema.adicionar_produto("Produto Teste", "Desc2", 200.00, 10)
        self.assertFalse(sucesso)
        self.assertIn("já existe", mensagem)
    
    def test_fazer_pedido_sucesso(self):
        """Testa fazer pedido com sucesso"""
        self.sistema.adicionar_produto("Produto", "Descrição", 100.00, 10)
        sucesso, mensagem = self.sistema.fazer_pedido(1, 3, "Pedido de teste")
        
        self.assertTrue(sucesso)
        self.assertIn("Pedido #1 realizado com sucesso", mensagem)
        self.assertIn("R$ 300.00", mensagem)
        
        # Verificar se pedido foi salvo e estoque atualizado
        produtos, historico = self.sistema._carregar_dados()
        self.assertEqual(len(historico), 1)
        self.assertEqual(historico.iloc[0]['quantidade_pedida'], 3)
        self.assertEqual(historico.iloc[0]['valor_total'], 300.00)
        self.assertEqual(historico.iloc[0]['status'], 'ativo')
        self.assertEqual(produtos.iloc[0]['quantidade_estoque'], 7)  # 10 - 3
    
    def test_fazer_pedido_validacoes(self):
        """Testa validações ao fazer pedido"""
        self.sistema.adicionar_produto("Produto", "Desc", 100.00, 5)
        
        # Quantidade zero
        sucesso, mensagem = self.sistema.fazer_pedido(1, 0)
        self.assertFalse(sucesso)
        self.assertIn("Quantidade deve ser maior que zero", mensagem)
        
        # Produto inexistente
        sucesso, mensagem = self.sistema.fazer_pedido(999, 1)
        self.assertFalse(sucesso)
        self.assertIn("não existe", mensagem)
        
        # Quantidade maior que estoque
        sucesso, mensagem = self.sistema.fazer_pedido(1, 10)
        self.assertFalse(sucesso)
        self.assertIn("Quantidade solicitada (10) maior que disponível (5)", mensagem)
        
        # Produto sem estoque
        self.sistema.adicionar_produto("Produto Sem Estoque", "Desc", 100.00, 0)
        sucesso, mensagem = self.sistema.fazer_pedido(2, 1)
        self.assertFalse(sucesso)
        self.assertIn("está fora de estoque", mensagem)
    
    def test_cancelar_pedido_sucesso(self):
        """Testa cancelamento de pedido com sucesso"""
        self.sistema.adicionar_produto("Produto", "Desc", 100.00, 10)
        self.sistema.fazer_pedido(1, 3, "Pedido teste")
        
        sucesso, mensagem = self.sistema.cancelar_pedido(1)
        
        self.assertTrue(sucesso)
        self.assertIn("cancelado com sucesso", mensagem)
        self.assertIn("estoque", mensagem.lower())
        
        # Verificar se pedido foi cancelado e estoque restaurado
        produtos, historico = self.sistema._carregar_dados()
        self.assertEqual(historico.iloc[0]['status'], 'cancelado')
        self.assertEqual(produtos.iloc[0]['quantidade_estoque'], 10)  # Restaurado
    
    def test_concorrencia_pedidos_simultaneos(self):
        """Testa atomicidade com pedidos concorrentes - teste crítico para thread safety"""
        self.sistema.adicionar_produto("Produto Limitado", "Desc", 100.00, 5)
        
        resultados = []
        
        def fazer_pedido(quantidade):
            sucesso, mensagem = self.sistema.fazer_pedido(1, quantidade)
            resultados.append((sucesso, mensagem))
        
        # Criar 3 threads tentando comprar 3 unidades cada (total 9, mas só tem 5)
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=fazer_pedido, args=(3,))
            threads.append(thread)
        
        # Iniciar todas as threads simultaneamente
        for thread in threads:
            thread.start()
        
        # Aguardar todas terminarem
        for thread in threads:
            thread.join()
        
        # Verificar resultados - apenas 1 deve ter sucesso
        sucessos = sum(1 for sucesso, _ in resultados if sucesso)
        falhas = sum(1 for sucesso, _ in resultados if not sucesso)
        
        self.assertLessEqual(sucessos, 1)
        self.assertGreaterEqual(falhas, 2)
        
        # Verificar integridade do estoque
        produtos, _ = self.sistema._carregar_dados()
        estoque_final = produtos.iloc[0]['quantidade_estoque']
        
        if sucessos == 1:
            self.assertEqual(estoque_final, 2)  # 5 - 3 = 2
        else:
            self.assertEqual(estoque_final, 5)  # Nenhum pedido processado

def executar_todos_os_testes():
    """Executa todos os testes e mostra relatório detalhado"""
    print("EXECUTANDO TESTES COMPLETOS DO SISTEMA")
    print("="*60)
    
    # Criar suite de testes
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSistemaPedidos)
    
    # Executar testes com relatório detalhado
    runner = unittest.TextTestRunner(verbosity=2)
    resultado = runner.run(suite)
    
    print("\n" + "="*60)
    print("RELATÓRIO FINAL DOS TESTES")
    print("="*60)
    print(f"Testes executados: {resultado.testsRun}")
    print(f"Falhas: {len(resultado.failures)}")
    print(f"Erros: {len(resultado.errors)}")
    
    if resultado.failures:
        print("\nFALHAS:")
        for teste, erro in resultado.failures:
            print(f"  - {teste}: {erro}")
    
    if resultado.errors:
        print("\nERROS:")
        for teste, erro in resultado.errors:
            print(f"  - {teste}: {erro}")
    
    if resultado.wasSuccessful():
        print("\nTODOS OS TESTES PASSARAM COM SUCESSO!")
    else:
        print(f"\n{len(resultado.failures + resultado.errors)} TESTES FALHARAM!")
    
    return resultado.wasSuccessful()

if __name__ == "__main__":
    executar_todos_os_testes()
