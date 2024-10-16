import os
import re
import logging

# Determinar o caminho absoluto para o diretório de logs, relativo a model.py
current_dir = os.path.dirname(os.path.abspath(__file__))
logs_dir = os.path.join(current_dir, '..', 'logs')

# Cria o diretório de logs se ele não existir
os.makedirs(logs_dir, exist_ok=True)

# Configuração básica de logging
log_file = os.path.join(logs_dir, 'app.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Node:
    """
    Classe que representa um nó na estrutura de arquivos. Pode ser um diretório ou arquivo.
    
    Atributos:
        - level: Nível do nó na hierarquia.
        - name: Nome do arquivo ou diretório.
        - is_dir: Indica se o nó é um diretório.
        - parent: Referência para o nó pai.
        - children: Lista de nós filhos (se for um diretório).
    """
    def __init__(self, level, name, is_dir=True, parent=None):
        self.level = level
        self.name = name
        self.is_dir = is_dir
        self.parent = parent
        self.children = [] if is_dir else None

    def add_child(self, child_node):
        """
        Adiciona um nó filho ao diretório atual.
        
        Args:
            - child_node: Instância da classe Node, representando o filho.
        """
        if self.is_dir:
            self.children.append(child_node)
            logging.info(f"Adicionado filho: {child_node.name} ao diretório {self.name}")

    def get_full_path(self):
        """
        Retorna o caminho completo do nó atual baseado na hierarquia.
        
        Returns:
            - Caminho completo do nó.
        """
        parts = []
        node = self
        while node:
            parts.insert(0, node.name)
            node = node.parent
        return os.path.join(*parts)

    def create_structure(self, base_path):
        """
        Cria a estrutura de diretórios e arquivos no sistema de arquivos.
        
        Args:
            - base_path: Diretório base onde a estrutura será criada.
        """
        full_path = os.path.join(base_path, self.get_full_path())
        if self.is_dir:
            if not os.path.exists(full_path):
                os.makedirs(full_path)
                logging.info(f"Diretório criado: {full_path}")
            for child in self.children:
                child.create_structure(base_path)
        else:
            # Verifica se o arquivo já existe antes de criar
            if not os.path.exists(full_path):
                with open(full_path, 'w', encoding='utf-8') as f:
                    pass  # Cria um arquivo vazio
                logging.info(f"Arquivo criado: {full_path}")
            else:
                logging.warning(f"Arquivo já existe: {full_path}")

class FileStructureModel:
    """
    Modelo responsável por gerenciar a estrutura de arquivos.
    """
    def __init__(self):
        self.root_nodes = []  # Lista de nós raiz

    def create_filesystem(self, base_path):
        """
        Cria a estrutura de arquivos no sistema de arquivos.
        
        Args:
            - base_path: Diretório base onde a estrutura será criada.
        """
        if self.root_nodes:
            for root_node in self.root_nodes:
                root_node.create_structure(base_path)
            logging.info(f"Estrutura de arquivos criada em: {base_path}")
        else:
            logging.warning("Nenhum nó raiz definido para criar a estrutura de arquivos.")

class NodeParserWithoutIndentationAndSymbols:
    """
    Classe responsável por processar a estrutura de arquivos sem indentação e sem símbolos.
    """
    def __init__(self):
        self.root_nodes = []  # Lista de nós raiz

    def build_structure(self, structure_lines):
        """
        Constrói a estrutura de arquivos com base em uma lista de linhas sem indentação e sem símbolos.
        
        Args:
            - structure_lines: Lista de strings representando a estrutura de arquivos.
        """
        logging.info("Construindo estrutura sem indentação e sem símbolos.")
        self.root_nodes = []
        for idx, line in enumerate(structure_lines, start=1):
            if not line.strip():
                continue

            name = line.strip()
            is_dir = name.endswith('/')
            if is_dir:
                name = name.rstrip('/')

            new_node = Node(0, name, is_dir)  # Nível zero (sem indentação)

            logging.info(f"Processando nó de nível zero: {name} (diretório: {is_dir})")
            self.root_nodes.append(new_node)

class NodeParserWithIndentationAndSymbols:
    """
    Classe responsável por processar a estrutura de arquivos com indentação e símbolos.
    """
    def __init__(self):
        self.root_nodes = []  # Lista de nós raiz

    def build_structure(self, structure_lines):
        """
        Constrói a estrutura de arquivos com base em uma lista de linhas que contém indentação e símbolos.
        
        Args:
            - structure_lines: Lista de strings representando a estrutura de arquivos.
        """
        logging.info("Construindo estrutura com indentação e símbolos.")
        self.root_nodes = []
        node_stack = []  # Pilha para controlar a hierarquia

        indent_pattern = re.compile(r'^(\s*)')  # Padrão para capturar a indentação (espaços ou tabs)

        for idx, line in enumerate(structure_lines, start=1):
            if not line.strip():
                continue

            # Remove os símbolos de árvore ├──, └──, │, etc.
            line_no_tree = re.sub(r'[├└─│]+', '', line).strip()
            indent_match = indent_pattern.match(line)
            indent = indent_match.group(1) if indent_match else ''
            level = len(indent) // 4  # Assume 4 espaços por nível de indentação

            name = line_no_tree.strip()

            if not name:
                logging.error(f"Linha {idx}: Nome do arquivo ou diretório está vazio.")
                raise ValueError(f"Linha {idx}: Nome do arquivo ou diretório está vazio.")

            is_dir = name.endswith('/')
            if is_dir:
                name = name.rstrip('/')

            new_node = Node(level, name, is_dir)

            logging.info(f"Processando nó: {name} (nível {level}, diretório: {is_dir})")

            if level == 0:
                # Nó raiz, adicionar diretamente à lista de nós raiz
                self.root_nodes.append(new_node)
                node_stack = [new_node]  # Reinicia a pilha com o novo nó raiz
                logging.info(f"Adicionado nó raiz: {name}")
            else:
                if not node_stack:
                    logging.error(f"Linha {idx}: Não há um nó pai para o nível {level}.")
                    raise ValueError(f"Linha {idx}: Não há um nó pai para o nível {level}.")

                # Remover nós da pilha até encontrar o nível correto
                while len(node_stack) > level:
                    popped_node = node_stack.pop()
                    logging.info(f"Removido nó da pilha: {popped_node.name}")

                if not node_stack:
                    logging.error(f"Linha {idx}: Estrutura de indentação inválida.")
                    raise ValueError(f"Linha {idx}: Estrutura de indentação inválida.")

                # O nó pai é o último na pilha
                parent_node = node_stack[-1]
                parent_node.add_child(new_node)
                new_node.parent = parent_node

                # Adicionar o novo nó à pilha
                node_stack.append(new_node)
