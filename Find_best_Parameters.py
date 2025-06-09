

import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

# Carregar os dados
file_path = 'C:/Users/ccerq/OneDrive/Documentos/Python Scripts/ML_CostAnalysis/Source_one_ML_WorKOrder_Cost_Analysis.csv'

try:
    df = pd.read_csv(file_path, sep=';', on_bad_lines='skip', encoding='utf-8')
    print("Arquivo lido com sucesso!")
except Exception as e:
    print(f"Erro ao ler o arquivo: {e}")

# Verificar as primeiras linhas do DataFrame para garantir que foi lido corretamente
print(df.head())

# Preservar as colunas identificadoras para referência
identifiers = df[['SEQ_KEY', 'ORDEM']]

# Pré-processamento dos dados
X = df.drop(['OUTCOME', 'SEQ_KEY', 'ORDEM'], axis=1)
y = df['OUTCOME']

# Codificação das variáveis categóricas
X = pd.get_dummies(X)

# Dividir em conjuntos de treinamento e teste, incluindo identificadores
X_train, X_test, y_train, y_test, identifiers_train, identifiers_test = train_test_split(X, y, identifiers, test_size=0.2, random_state=42)

# Normalizar os dados
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Definir a grade de hiperparâmetros
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_features': ['auto', 'sqrt', 'log2'],
    'max_depth': [10, 20, 30, None],
    'criterion': ['gini', 'entropy']
}

# Inicializar o modelo RandomForest
rf = RandomForestClassifier(random_state=42)

# Inicializar o GridSearchCV
grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv=5, n_jobs=-1, verbose=2)

# Executar o Grid Search
grid_search.fit(X_train, y_train)

# Exibir os melhores parâmetros
print("Melhores parâmetros encontrados: ", grid_search.best_params_)

# Treinar o modelo com os melhores parâmetros
best_rf = grid_search.best_estimator_
best_rf.fit(X_train, y_train)

# Previsões
y_pred = best_rf.predict(X_test)

# Avaliar o modelo
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))

# Converter X_test de volta para DataFrame para identificar registros
X_test_df = pd.DataFrame(X_test, columns=X.columns)

# Adicionar as previsões e os rótulos verdadeiros ao DataFrame
X_test_df['True_OUTCOME'] = y_test.values
X_test_df['Predicted_OUTCOME'] = y_pred

# Restaurar os identificadores
X_test_df = pd.concat([identifiers_test.reset_index(drop=True), X_test_df.reset_index(drop=True)], axis=1)

# Identificar registros classificados incorretamente
incorrect_classifications = X_test_df[X_test_df['True_OUTCOME'] != X_test_df['Predicted_OUTCOME']]

# Mostrar os registros incorretamente classificados
print(incorrect_classifications)

# Salvar os registros incorretamente classificados em um arquivo CSV
output_file_path = 'C:/Users/ccerq/OneDrive/Documentos/Python Scripts/ML_CostAnalysis/incorrect_classifications.csv'
incorrect_classifications.to_csv(output_file_path, index=False)
print(f"Arquivo salvo em: {output_file_path}")
