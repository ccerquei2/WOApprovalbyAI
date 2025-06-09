import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib

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

# Salvar o scaler para uso futuro
joblib.dump(scaler, 'C:/Users/ccerq/OneDrive/Documentos/Python Scripts/ML_CostAnalysis/scaler.joblib')


# Treinar o modelo com os melhores parâmetros
best_rf = RandomForestClassifier(
    criterion='gini',
    max_depth=10,
    max_features='sqrt',
    n_estimators=300,
    random_state=42
)
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

# Salvar o modelo treinado para uso futuro
model_file_path = 'C:/Users/ccerq/OneDrive/Documentos/Python Scripts/ML_CostAnalysis/best_random_forest_model.joblib'
joblib.dump(best_rf, model_file_path)
print(f"Modelo salvo em: {model_file_path}")


