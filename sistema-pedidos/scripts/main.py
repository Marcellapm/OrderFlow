import pandas as pd
import threading
from datetime import datetime
import os

class SistemaPedidos:
    def __init__(self, arquivo_excel='dados/sistema_pedidos.xlsx'):
        # Lock para garantir atomicidade em operações concorrentes
        self.lock = threading.Lock()
        
        # Arquivo único do sistema
        self.arquivo_excel = arquivo_excel
        
        # Criar pasta se não existir
        pasta = os.path.dirname(arquivo_excel)
        if pasta:
            os.makedirs(pasta, exist_ok=True)
        
        # Inicializar arquivo se não existir
        self._inicializar_arquivo()
    
    def _inicializar_arquivo(self):
        """Cria arquivo Excel com duas abas se não existir"""
        if not os.path.exists(self.arquivo_excel):
            # Aba de produtos (vazia inicialmente)
            produtos_df = pd.DataFrame(columns=[
                'id_produto', 'nome', 'descricao', 'preco_unitario', 'quantidade_estoque'
            ])
            
            # Aba de histórico de pedidos (vazia inicialmente)
            historico_df = pd.DataFrame(columns=[
                'id_pedido', 'id_produto', 'nome_produto', 'descricao_pedido', 
                'quantidade_pedida', 'preco_unitario', 'valor_total', 
                'data_pedido', 'status'
            ])
            
            # Salvar arquivo com duas abas
            with pd.ExcelWriter(self.arquivo_excel, engine='openpyxl') as writer:
                produtos_df.to_excel(writer, sheet_name='Produtos', index=False)
                historico_df.to_excel(writer, sheet_name='Historico', index=False)
    
    def _carregar_dados(self):
        """Carrega dados das duas abas do Excel"""
        try:
            produtos = pd.read_excel(self.arquivo_excel, sheet_name='Produtos')
            historico = pd.read_excel(self.arquivo_excel, sheet_name='Historico')
            return produtos, historico
        except Exception as e:
            raise Exception(f"Erro ao carregar dados: {e}")
    
    def _salvar_dados(self, produtos, historico):
        """Salva dados nas duas abas do Excel"""
        try:
            with pd.ExcelWriter(self.arquivo_excel, engine='openpyxl') as writer:
                produtos.to_excel(writer, sheet_name='Produtos', index=False)
                historico.to_excel(writer, sheet_name='Historico', index=False)
        except Exception as e:
            raise Exception(f"Erro ao salvar dados: {e}")
    
    def adicionar_produto(self, nome, descricao, preco_unitario, quantidade_estoque):
        """Adiciona um novo produto ao sistema"""
        # Lock necessário para evitar IDs duplicados em operações concorrentes
        with self.lock:
            produtos, historico = self._carregar_dados()
            
            # Validações de entrada
            if not nome or not nome.strip():
                return False, "Nome do produto não pode estar vazio!"
            
            if preco_unitario <= 0:
                return False, "Preço deve ser maior que zero!"
            
            if quantidade_estoque < 0:
                return False, "Quantidade em estoque não pode ser negativa!"
            
            # Verificar se produto já existe (case insensitive)
            if not produtos.empty and nome.strip().lower() in produtos['nome'].str.lower().values:
                return False, f"Produto '{nome}' já existe!"
            
            # Gerar novo ID sequencial
            novo_id = 1 if produtos.empty else int(produtos['id_produto'].max()) + 1
            
            # Adicionar produto
            novo_produto = pd.DataFrame([{
                'id_produto': novo_id,
                'nome': nome.strip(),
                'descricao': descricao.strip() if descricao else '',
                'preco_unitario': preco_unitario,
                'quantidade_estoque': quantidade_estoque
            }])
            
            produtos = pd.concat([produtos, novo_produto], ignore_index=True)
            
            # Salvar alterações
            self._salvar_dados(produtos, historico)
            
            return True, f"Produto '{nome}' adicionado com sucesso! ID: {novo_id}"
    
    def listar_estoque(self):
        """Lista produtos disponíveis em estoque"""
        produtos, _ = self._carregar_dados()
        
        if produtos.empty:
            print("\nNenhum produto cadastrado no sistema.")
            return pd.DataFrame()
        
        # Filtrar apenas produtos com estoque > 0
        produtos_disponiveis = produtos[produtos['quantidade_estoque'] > 0].copy()
        
        print("\nESTOQUE DISPONIVEL")
        print("=" * 80)
        
        if produtos_disponiveis.empty:
            print("Nenhum produto disponível em estoque.")
            return pd.DataFrame()
        
        for _, produto in produtos_disponiveis.iterrows():
            print(f"ID: {int(produto['id_produto'])} | "
                  f"{produto['nome']} | "
                  f"R$ {produto['preco_unitario']:.2f} | "
                  f"Estoque: {int(produto['quantidade_estoque'])} unidades")
            if produto['descricao']:
                print(f"   Descrição: {produto['descricao']}")
            print("-" * 80)
        
        return produtos_disponiveis
    
    def fazer_pedido(self, id_produto, quantidade_pedida, descricao_pedido=""):
        """Faz um pedido de produto"""
        
        # Validação básica antes do lock
        if quantidade_pedida <= 0:
            return False, "Quantidade deve ser maior que zero!"
        
        # Lock crítico para garantir atomicidade da operação
        with self.lock:
            produtos, historico = self._carregar_dados()
            
            # Validação: Produto existe?
            if produtos.empty or id_produto not in produtos['id_produto'].values:
                return False, f"Produto com ID {id_produto} não existe!"
            
            produto = produtos[produtos['id_produto'] == id_produto].iloc[0]
            
            # Validação: Quantidade disponível em estoque?
            quantidade_disponivel = int(produto['quantidade_estoque'])
            
            if quantidade_disponivel == 0:
                return False, f"Produto '{produto['nome']}' está fora de estoque!"
            
            if quantidade_pedida > quantidade_disponivel:
                return False, f"Quantidade solicitada ({quantidade_pedida}) maior que disponível ({quantidade_disponivel})!"
            
            # Criar o pedido
            novo_id_pedido = 1 if historico.empty else int(historico['id_pedido'].max()) + 1
            valor_total = quantidade_pedida * produto['preco_unitario']
            
            novo_pedido = pd.DataFrame([{
                'id_pedido': novo_id_pedido,
                'id_produto': id_produto,
                'nome_produto': produto['nome'],
                'descricao_pedido': descricao_pedido if descricao_pedido else f"Pedido de {quantidade_pedida}x {produto['nome']}",
                'quantidade_pedida': quantidade_pedida,
                'preco_unitario': produto['preco_unitario'],
                'valor_total': valor_total,
                'data_pedido': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'ativo'
            }])
            
            # Adicionar pedido ao histórico
            historico = pd.concat([historico, novo_pedido], ignore_index=True)
            
            # Atualizar estoque (operação crítica)
            produtos.loc[produtos['id_produto'] == id_produto, 'quantidade_estoque'] -= quantidade_pedida
            
            # Salvar todas as alterações atomicamente
            self._salvar_dados(produtos, historico)
            
            return True, f"Pedido #{novo_id_pedido} realizado com sucesso!\n" \
                        f"   Produto: {produto['nome']}\n" \
                        f"   Quantidade: {quantidade_pedida}\n" \
                        f"   Valor total: R$ {valor_total:.2f}"
    
    def ver_historico(self, apenas_ativos=False):
        """Mostra histórico de pedidos"""
        _, historico = self._carregar_dados()
        
        if historico.empty:
            print("\nNenhum pedido encontrado no histórico.")
            return pd.DataFrame()
        
        # Filtrar se necessário
        if apenas_ativos:
            pedidos_filtrados = historico[historico['status'] == 'ativo']
            titulo = "PEDIDOS ATIVOS"
        else:
            pedidos_filtrados = historico
            titulo = "HISTÓRICO COMPLETO DE PEDIDOS"
        
        if pedidos_filtrados.empty:
            print(f"\n{titulo}")
            print("=" * 80)
            print("Nenhum pedido encontrado.")
            return pd.DataFrame()
        
        print(f"\n{titulo}")
        print("=" * 80)
        
        for _, pedido in pedidos_filtrados.iterrows():
            status_symbol = "[ATIVO]" if pedido['status'] == 'ativo' else "[CANCELADO]"
            print(f"{status_symbol} Pedido #{int(pedido['id_pedido'])} | "
                  f"{pedido['nome_produto']} | "
                  f"Qtd: {int(pedido['quantidade_pedida'])} | "
                  f"R$ {pedido['valor_total']:.2f}")
            print(f"   Descrição: {pedido['descricao_pedido']}")
            print(f"   Data: {pedido['data_pedido']} | Status: {pedido['status'].upper()}")
            print("-" * 80)
        
        return pedidos_filtrados
    
    def cancelar_pedido(self, id_pedido):
        """Cancela um pedido e restaura o estoque"""
        # Lock necessário para operação atômica de cancelamento
        with self.lock:
            produtos, historico = self._carregar_dados()
            
            if historico.empty:
                return False, "Nenhum pedido encontrado!"
            
            # Encontrar o pedido
            pedido_mask = historico['id_pedido'] == id_pedido
            if not pedido_mask.any():
                return False, f"Pedido #{id_pedido} não encontrado!"
            
            pedido = historico[pedido_mask].iloc[0]
            
            if pedido['status'] != 'ativo':
                return False, f"Pedido #{id_pedido} já foi cancelado!"
            
            # Cancelar pedido
            historico.loc[pedido_mask, 'status'] = 'cancelado'
            
            # Restaurar estoque (operação crítica)
            produtos.loc[produtos['id_produto'] == pedido['id_produto'], 'quantidade_estoque'] += pedido['quantidade_pedida']
            
            # Salvar alterações atomicamente
            self._salvar_dados(produtos, historico)
            
            return True, f"Pedido #{id_pedido} cancelado com sucesso!\n" \
                        f"   Estoque de '{pedido['nome_produto']}' foi restaurado."
    
    def obter_estatisticas(self):
        """Retorna estatísticas do sistema"""
        produtos, historico = self._carregar_dados()
        
        stats = {
            'total_produtos': len(produtos),
            'produtos_em_estoque': len(produtos[produtos['quantidade_estoque'] > 0]) if not produtos.empty else 0,
            'produtos_sem_estoque': len(produtos[produtos['quantidade_estoque'] == 0]) if not produtos.empty else 0,
            'total_pedidos': len(historico),
            'pedidos_ativos': len(historico[historico['status'] == 'ativo']) if not historico.empty else 0,
            'pedidos_cancelados': len(historico[historico['status'] == 'cancelado']) if not historico.empty else 0,
            'valor_total_pedidos_ativos': historico[historico['status'] == 'ativo']['valor_total'].sum() if not historico.empty else 0,
            'valor_total_geral': historico['valor_total'].sum() if not historico.empty else 0
        }
        
        return stats

def menu_principal():
    """Interface principal do sistema"""
    sistema = SistemaPedidos()
    
    while True:
        print("\n" + "=" * 60)
        print("SISTEMA DE GERENCIAMENTO DE PEDIDOS")
        print("=" * 60)
        print("1. Listar estoque disponível")
        print("2. Fazer pedido")
        print("3. Ver histórico de pedidos")
        print("4. Cancelar pedido")
        print("5. Adicionar produto (Admin)")
        print("6. Ver estatísticas")
        print("7. Sair")
        print("-" * 60)
        
        try:
            opcao = input("Escolha uma opção (1-7): ").strip()
            
            if opcao == '1':
                sistema.listar_estoque()
            
            elif opcao == '2':
                produtos_disponiveis = sistema.listar_estoque()
                if not produtos_disponiveis.empty:
                    print("\nFAZER PEDIDO")
                    print("-" * 30)
                    id_produto = int(input("Digite o ID do produto: "))
                    quantidade = int(input("Digite a quantidade desejada: "))
                    descricao = input("Digite uma descrição para o pedido (opcional): ").strip()
                    
                    sucesso, mensagem = sistema.fazer_pedido(id_produto, quantidade, descricao)
                    print(f"\n{mensagem}")
            
            elif opcao == '3':
                print("\nOPÇÕES DE HISTÓRICO")
                print("1. Ver apenas pedidos ativos")
                print("2. Ver histórico completo")
                
                sub_opcao = input("Escolha (1-2): ").strip()
                if sub_opcao == '1':
                    sistema.ver_historico(apenas_ativos=True)
                elif sub_opcao == '2':
                    sistema.ver_historico(apenas_ativos=False)
                else:
                    print("Opção inválida!")
            
            elif opcao == '4':
                pedidos_ativos = sistema.ver_historico(apenas_ativos=True)
                if not pedidos_ativos.empty:
                    print("\nCANCELAR PEDIDO")
                    print("-" * 30)
                    id_pedido = int(input("Digite o ID do pedido para cancelar: "))
                    sucesso, mensagem = sistema.cancelar_pedido(id_pedido)
                    print(f"\n{mensagem}")
            
            elif opcao == '5':
                print("\nADICIONAR PRODUTO")
                print("-" * 30)
                nome = input("Nome do produto: ").strip()
                descricao = input("Descrição do produto: ").strip()
                preco = float(input("Preço unitário: R$ "))
                quantidade = int(input("Quantidade inicial em estoque: "))
                
                sucesso, mensagem = sistema.adicionar_produto(nome, descricao, preco, quantidade)
                print(f"\n{mensagem}")
            
            elif opcao == '6':
                stats = sistema.obter_estatisticas()
                print("\nESTATÍSTICAS DO SISTEMA")
                print("=" * 50)
                print(f"Total de produtos cadastrados: {stats['total_produtos']}")
                print(f"Produtos em estoque: {stats['produtos_em_estoque']}")
                print(f"Produtos sem estoque: {stats['produtos_sem_estoque']}")
                print(f"Total de pedidos: {stats['total_pedidos']}")
                print(f"Pedidos ativos: {stats['pedidos_ativos']}")
                print(f"Pedidos cancelados: {stats['pedidos_cancelados']}")
                print(f"Valor pedidos ativos: R$ {stats['valor_total_pedidos_ativos']:.2f}")
                print(f"Valor total geral: R$ {stats['valor_total_geral']:.2f}")
            
            elif opcao == '7':
                print("\nObrigado por usar o sistema!")
                break
            
            else:
                print("\nOpção inválida! Tente novamente.")
                
        except ValueError:
            print("\nErro: Digite apenas números válidos!")
        except KeyboardInterrupt:
            print("\n\nSistema encerrado pelo usuário!")
            break
        except Exception as e:
            print(f"\nErro inesperado: {e}")

if __name__ == "__main__":
    menu_principal()
