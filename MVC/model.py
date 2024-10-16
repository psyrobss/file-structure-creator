import os
import re
import logging

class Node:
    """
    Classe que representa um nó hierárquico (diretório ou arquivo).
    """
    def __init__(self, level, name, is_dir=True, parent=None):
        self.level = level
        self.name = name  # Nome do diretório ou arquivo
        self.is_dir = is_dir  # True se for diretório, False se for arquivo
        self.parent = parent  # Nó pai (None se for o nó raiz)
        self.children = [] if is_dir else None  # Lista de filhos (se for diretório)

    def add_child(self, child_node):
        """
        Adiciona um nó filho ao diretório (nó pai).
        """
        if self.is_dir:
            self.children.append(child_node)
            logging.info(f"Adicionado filho: {child_node.name} ao diretório {self.name}")

    def get_level(self):
        """
        Retorna o nível do nó com base na profundidade na hierarquia.
        """
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level

    def get_full_path(self):
        """
        Retorna o caminho completo para o nó atual, com base na hierarquia.
        """
        parts = []
        node = self
        while node:
            parts.insert(0, node.name)  # Inserir no início da lista para montar o caminho
            node = node.parent
        return os.path.join(*parts)

    def create_structure(self, base_path):
        """
        Cria a estrutura de arquivos e diretórios no sistema de arquivos.
        """
        full_path = os.path.join(base_path, self.get_full_path())
        if self.is_dir:
            if not os.path.exists(full_path):
                os.makedirs(full_path)
                logging.info(f"Diretório criado: {full_path}")
            for child in self.children:
                child.create_structure(base_path)
        else:
            with open(full_path, 'w', encoding='utf-8') as f:
                pass  # Cria um arquivo vazio
            logging.info(f"Arquivo criado: {full_path}")

class FileStructureModel:
    """
    Modelo para gerenciamento da estrutura de arquivos e pastas.
    """
    def __init__(self):
        self.root_nodes = []  # Lista de nós raiz

    def build_structure(self, structure_lines):
        """
        Constrói a estrutura de arquivos com base em uma lista de linhas que representa a hierarquia.
        """
        logging.info("Iniciando a construção da estrutura de arquivos...")
        self.root_nodes = []
        node_stack = []  # Pilha para controlar a hierarquia

        indent_pattern = re.compile(r'^( *)')  # Padrão para capturar a indentação

        for idx, line in enumerate(structure_lines, start=1):
            if not line.strip():
                continue

            # Remove os símbolos de árvore ├──, └──, │, etc.
            line_no_tree = re.sub(r'[├└─│]+', '', line)
            indent_match = indent_pattern.match(line_no_tree)
            indent = indent_match.group(1) if indent_match else ''
            level = len(indent) // 4  # Assume 4 espaços por nível de indentação

            name = line_no_tree.strip()

            if not name:
                raise ValueError(f"Linha {idx}: Nome do arquivo ou diretório está vazio.")

            is_dir = name.endswith('/')
            if is_dir:
                name = name.rstrip('/')

            new_node = Node(level, name, is_dir)

            logging.info(f"Processando nó: {name} (nível {level}, diretório: {is_dir})")

            if level == 0:
                self.root_nodes.append(new_node)
                node_stack = [new_node]
                logging.info(f"Adicionado nó raiz: {name}")
            else:
                if not node_stack:
                    raise ValueError(f"Linha {idx}: Não há um nó pai para o nível {level}.")
                while len(node_stack) > level:
                    popped_node = node_stack.pop()
                    logging.info(f"Removido nó da pilha: {popped_node.name}")

                if not node_stack:
                    raise ValueError(f"Linha {idx}: Estrutura de indentação inválida.")

                parent_node = node_stack[-1]
                parent_node.add_child(new_node)
                new_node.parent = parent_node

                node_stack.append(new_node)

    def create_filesystem(self, base_path):
        """
        Cria a estrutura de arquivos no sistema de arquivos.
        """
        if self.root_nodes:
            for root_node in self.root_nodes:
                root_node.create_structure(base_path)
