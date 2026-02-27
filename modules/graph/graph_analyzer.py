import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO
from typing import List, Dict

class GraphAnalyzer:
    def __init__(self):
        self.graph = nx.DiGraph()
    
    def build_graph(self, transactions: List[Dict]):
        """Строит граф транзакций"""
        for tx in transactions:
            from_addr = tx.get('from')
            to_addr = tx.get('to')
            value = float(tx.get('value', 0))
            
            if from_addr and to_addr:
                if self.graph.has_edge(from_addr, to_addr):
                    self.graph[from_addr][to_addr]['weight'] += value
                else:
                    self.graph.add_edge(from_addr, to_addr, weight=value)
    
    def get_metrics(self):
        """Возвращает метрики графа"""
        metrics = {
            'node_count': self.graph.number_of_nodes(),
            'edge_count': self.graph.number_of_edges(),
            'density': nx.density(self.graph),
            'clustering_coefficient': nx.average_clustering(self.graph.to_undirected()),
            'degree_centrality': nx.degree_centrality(self.graph),
        }
        # Поиск сообществ (например, алгоритм Лувена)
        try:
            from community import community_louvain
            partition = community_louvain.best_partition(self.graph.to_undirected())
            metrics['communities'] = len(set(partition.values()))
        except ImportError:
            pass
        return metrics
    
    def detect_suspicious_patterns(self):
        """Выявляет подозрительные паттерны (кольца, звезды)"""
        suspicious = []
        # Поиск циклических структур (возможные отмывочные схемы)
        cycles = list(nx.simple_cycles(self.graph))
        if cycles:
            suspicious.append(f"Обнаружено {len(cycles)} циклов")
        
        # Поиск узлов с высокой степенью (хабы)
        degree = dict(self.graph.degree())
        high_degree = [node for node, deg in degree.items() if deg > 10]
        if high_degree:
            suspicious.append(f"Узлы с высокой связностью: {high_degree[:5]}")
        
        return suspicious
    
    def generate_plot(self) -> BytesIO:
        """Генерирует изображение графа (упрощённо)"""
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(self.graph, k=0.5)
        nx.draw(self.graph, pos, with_labels=False, node_size=50, node_color='blue', edge_color='gray', alpha=0.6)
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        return buf
