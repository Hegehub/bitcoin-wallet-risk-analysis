import joblib
import numpy as np
from typing import Dict, List
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

class MLRiskPredictor:
    def __init__(self, model_path: str = None):
        self.model = None
        if model_path:
            self.load_model(model_path)
        self.feature_names = ['tx_count', 'avg_amount', 'unique_contracts', 'origin_risk', 
                              'night_activity', 'mixer_interactions', 'graph_centrality']
    
    def load_model(self, path: str):
        self.model = joblib.load(path)
    
    def save_model(self, path: str):
        joblib.dump(self.model, path)
    
    def extract_features(self, wallet_data: Dict) -> np.ndarray:
        """Извлекает признаки из данных кошелька"""
        features = [
            wallet_data.get('transaction_count', 0),
            wallet_data.get('avg_amount', 0),
            wallet_data.get('unique_contracts', 0),
            wallet_data.get('origin_risk', 50) / 100,  # нормализация
            wallet_data.get('night_activity_ratio', 0),
            wallet_data.get('mixer_interactions', 0),
            wallet_data.get('graph_centrality', 0)
        ]
        return np.array(features).reshape(1, -1)
    
    def predict_risk(self, wallet_data: Dict) -> float:
        """Возвращает вероятность риска от 0 до 100"""
        if self.model is None:
            return 50.0  # дефолт
        features = self.extract_features(wallet_data)
        proba = self.model.predict_proba(features)[0][1]
        return proba * 100
    
    def train(self, X: pd.DataFrame, y: pd.Series, test_size=0.2):
        """Обучение модели"""
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)
        self.model = RandomForestClassifier(n_estimators=100, max_depth=10)
        self.model.fit(X_train, y_train)
        score = self.model.score(X_test, y_test)
        print(f"Model accuracy: {score}")
        return score
