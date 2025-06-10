from crewai import Agent, Task, Crew
from langchain_groq import ChatGroq
import pyodbc
import pandas as pd
import joblib
from decrypt import decrypt_keys

# Configurar o modelo LLM ChatGroq com Mixtral
llm = ChatGroq(

    api_key=decrypt_keys("groq_api_key"),
    model="mixtral-8x7b-32768"
)

class AnaliseErros:
    def __init__(self):
        self.server = 'DBDEV'
        self.database = 'JDE_CRP'
        self.username = decrypt_keys("user_diretas")
        self.password = decrypt_keys("password_diretas")


    def cria_Conn(self):
        conn_str = f'DRIVER={{SQL Server}};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}'
        try:
            conn = pyodbc.connect(conn_str)
            return conn
        except Exception as e:
            print("Error to connect to the database:", e)
            return None



    def extrair_dados(self, SEQ_KEY):
        query = f"""
        SELECT
            SEQ_KEY, ORDEM, VARIACAO_IMXIC, DIF_CUSTO_P_x_R, MAT_DIF_PERCENTUAL,
            TAXA_MAQUINA_FIXA, TAXA_MO_FIXA, TAXA_FIXA_VAR_MO, MO_VALOR, HR_MAQ_VALOR,
            HR_EXC_VLR, HR_CONFIG_VLR, MO_VARIACAO, EXTERNA_OPERACAO
        FROM  CRPDTA.FNML481
        WHERE SEQ_KEY = {SEQ_KEY}
        ORDER BY ORDEM, SEQ_KEY
        """
        conn = self.cria_Conn()
        if conn:
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        else:
            return None

    def preprocess_data(self, df):
        identifiers = df[['SEQ_KEY', 'ORDEM']]
        df = df.drop(['SEQ_KEY', 'ORDEM'], axis=1)
        df = pd.get_dummies(df)
        scaler = joblib.load('C:/Users/ccerq/OneDrive/Documentos/Python Scripts/ML_CostAnalysis/scaler.joblib')
        df_normalized = scaler.transform(df)
        return df_normalized, identifiers

    def classificar_ordem(self, df):
        model = joblib.load('C:/Users/ccerq/OneDrive/Documentos/Python Scripts/ML_CostAnalysis/best_random_forest_model.joblib')
        df_normalized, identifiers = self.preprocess_data(df)
        predictions = model.predict(df_normalized)
        df['Predicted_OUTCOME'] = predictions
        result_df = pd.concat([identifiers.reset_index(drop=True), df.reset_index(drop=True)], axis=1)
        return result_df

    def buscar_justificativa_fabrica(self, SEQ_KEY):
        justificativas = pd.read_csv('C:/Users/ccerq/OneDrive/Documentos/Python Scripts/ML_CostAnalysis/justificativa Fabrica.csv')
        justificativa = justificativas[justificativas['SEQ_KEY'] == SEQ_KEY]
        if not justificativa.empty:
            return justificativa.iloc[0]['JUSTIFICATIVA']
        else:
            return None

    def validar_justificativa(self, justificativa, df):
        if 'aumento no custo de material' in justificativa.lower() and df['MAT_DIF_PERCENTUAL'].iloc[0] > 0:
            return True
        return False

analise_erros = AnaliseErros()


from crewai_tools import CSVSearchTool

# Agente para buscar justificativas
csv_tool = CSVSearchTool(filepath='C:/Users/ccerq/OneDrive/Documentos/Python Scripts/ML_CostAnalysis/justificativa Fabrica.csv')

justificativa_agent = Agent(
    role='Justificativa Finder',
    goal='Buscar e validar justificativas da fábrica',
    tools=[csv_tool],
    verbose=True,
    llm=llm
)

# Tarefa de buscar justificativa
buscar_justificativa_task = Task(
    description='Buscar justificativa da fábrica para SEQ_KEY específica',
    expected_output='Justificativa correspondente à SEQ_KEY',
    agent=justificativa_agent
)

# Agente para processar a ordem
processar_ordem_agent = Agent(
    role='Order Processor',
    goal='Classificar e aprovar ou suspender ordens com base na justificativa da fábrica',
    backstory='Um agente especializado em análise de erros e validação de ordens',
    verbose=True,
    llm=llm
)

# Função para processar a ordem
def processar_ordem_task_fn(SEQ_KEY):
    df = analise_erros.extrair_dados(SEQ_KEY)
    if df is not None:
        resultado = analise_erros.classificar_ordem(df)
        classificacao = resultado['Predicted_OUTCOME'].iloc[0]
        if classificacao == 'REQUER JUSTIFICATIVA FABRICA':
            justificativa = buscar_justificativa_task.execute(SEQ_KEY=SEQ_KEY)
            if justificativa and analise_erros.validar_justificativa(justificativa, df):
                print(f"Ordem {SEQ_KEY} aprovada com justificativa: {justificativa}")
            else:
                print(f"Ordem {SEQ_KEY} não aprovada. Justificativa inconsistente ou não encontrada.")
        else:
            print(f"Ordem {SEQ_KEY} aprovada automaticamente. Classificação: {classificacao}")
    else:
        print("Falha ao extrair dados.")

processar_ordem_task = Task(
    description='Processar ordem de produção',
    agent=processar_ordem_agent,
    task_fn=processar_ordem_task_fn
)

# Criar e executar o crew
crew = Crew(
    agents=[justificativa_agent, processar_ordem_agent],
    tasks=[buscar_justificativa_task, processar_ordem_task],
    verbose=2
)

crew.kickoff()


