

import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import joblib
import json
from load_environment import ConfigLoader
from decrypt import decrypt_keys

class Analise:

    def __init__(self, environment='dev'):
        config_loader = ConfigLoader(environment)
        db_config = config_loader.get_database_config()
        self.server = db_config['server']
        self.database = db_config['database']
        self.username = decrypt_keys("user_diretas")
        self.password = decrypt_keys("password_diretas")
        self.schema_main = db_config['schema_main']
        self.schema_udc = db_config['schema_udc']
        self.root_path = os.path.dirname(os.path.abspath(__file__))

    def cria_Conn(self):
        connection_string = (
            f"DRIVER={{SQL Server}};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password}"
        )
        connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})
        engine = create_engine(connection_url)
        return engine



    def justificativa_fabrica(self, SEQ_KEY, ORDEM):
        query = f"""                
                /*******************************************************************************************************
                1 - Validar se ordem não tem variações totais que impossibiltam a aprovaçção do custo
                2 - Se predição determinar que a Fabrica Deverá justificar 	a variação, 
                    "REQUER JUSTIFICATI FABRICA" o sistema deverá verificar se há variação de quantidades na ordem.
                3 - Caso não haja variação de quantidade a ordem deverá ser direcinada para o fluxo, 
                    "APROVADO COM JUSTIFICATIVA SETOR CUSTOS".
                *******************************************************************************************************/
                SELECT  
                        Top 1   
                        Acao = MAX(FAIXAS.Ação),
                        ORDEM = VALORES.ORDEM,
                        FAIXAS.Outcome,
                        Descriçao_Ação = (SELECT TOP 1 DESCFAIXAS.Descriçao_Ação FROM {self.schema_main}.FNML481L DESCFAIXAS WHERE MAX(FAIXAS.Ação) = DESCFAIXAS.Ação),
                        VARIACAO_IMXIC				= MAX(ABS(VALORES.VARIACAO_IMXIC)),    
                        LIMITE_VARIACAO_IMXIC		= LIMITE.VARIACAO_IMXIC,

                        VARIACAO_QTD_TOTAL			= MAX(VAR_QTD_TOTAL),
                        LIMITE_VARIACAO_MAT_QTD		= LIMITE.VAR_MAT_QTD,

                        VARIACAO_VALOR_REF_IM		= MAX(VAR_VALOR_REF_IM),
                        LIMITE_VARIACAO_MAT_VLR		= LIMITE.VAR_MAT_VLR,

                        VARIACAO_PERCENT			= MAX(VAR_PERCENT),				
                        LIMITE_VARIACAO_HRS_VLR		= LIMITE.VAR_HRS_VLR,

                        ERRO_CRITICO				= MAX(ERRO_CRITICO)

                    FROM  
                            {self.schema_main}.FNML481 VALORES,
                            {self.schema_main}.FNML481L FAIXAS
                            LEFT JOIN 
                            {self.schema_main}.FNML481L LIMITE ON
                            LIMITE.AÇÃO IN ('1') AND
                            LIMITE.Outcome = FAIXAS.Outcome

                    WHERE	             
                            VALORES.SEQ_KEY = {SEQ_KEY} AND
                            VALORES.ORDEM = {ORDEM} AND                            
                            FAIXAS.Outcome = 'REQUER JUSTIFICATIVA FABRICA'       
                    GROUP BY 
                            FAIXAS.Outcome,
                            VALORES.ORDEM,
                            LIMITE.VARIACAO_IMXIC,
                            LIMITE.VAR_MAT_QTD,
                            LIMITE.VAR_MAT_VLR,
                            LIMITE.VAR_HRS_VLR
                    HAVING 
                            (MAX(VAR_QTD_TOTAL) >= LIMITE.VAR_MAT_QTD AND MAX(VAR_VALOR_REF_IM) >= LIMITE.VAR_MAT_VLR) --Variação de Quantidade só deve ser considerada se for acompanhada de variação de valor.
                            OR 		
                             MAX(VAR_PERCENT) >= LIMITE.VAR_HRS_VLR --Quantidades de horas que repercurtiram em variação de valor.
                """
        engine = self.cria_Conn()
        if engine:
            df = pd.read_sql(query, engine)
            engine.dispose()
            return df
        else:
            return None



    def extrair_dados(self, SEQ_KEY, ORDEM):
        query = f"""
        SELECT 
            SEQ_KEY, ORDEM, VARIACAO_IMXIC = ABS(VARIACAO_IMXIC), DIF_CUSTO_P_x_R, MAT_DIF_PERCENTUAL, 
            TAXA_MAQUINA_FIXA, TAXA_MO_FIXA, TAXA_FIXA_VAR_MO, MO_VALOR, HR_MAQ_VALOR, 
            HR_EXC_VLR, HR_CONFIG_VLR, MO_VARIACAO, EXTERNA_OPERACAO 
        FROM  {self.schema_main}.FNML481
        WHERE 
            SEQ_KEY = {SEQ_KEY} AND
            ORDEM = {ORDEM}
        ORDER BY ORDEM, SEQ_KEY
        """
        engine = self.cria_Conn()
        if engine:
            df = pd.read_sql(query, engine)
            engine.dispose()
            return df
        else:
            return None




    def extrair_dados_qtd(self, SEQ_KEY, ORDEM):
        query = f"""
                    SELECT 
                            [Seq_Key]							= A.SEQ_KEY,
                            [Ordem]								= A.ORDEM,
                            [Variação_Quantidade]				= ROUND(A.VAR_QTD_TOTAL*100,2),
                            [Variação_Valor_Total_Quantidade]	= ROUND(A.VAR_VALOR_REF_IM*100,2),
                            [Diferença_Hora_Maquina]			= B.DIF_HR_MAQUINA,	
                            [Diferença_Hora_Execução]			= B.DIF_HR_EXECUCAO,	
                            [Diferença_Hora_Configuração]		= B.DIF_HR_CONFIG,
                            [Variação_Valor_Total_Horas]		= ROUND(B.VAR_PERCENT*100,2)
                    FROM 
                        {self.schema_main}.FNML48FB A WITH(NOLOCK)   
                    INNER JOIN 
                        {self.schema_main}.FNML48CB B WITH(NOLOCK)  ON 
                        A.SEQ_KEY = B.SEQ_KEY AND 
                        A.ORDEM = B.ORDEM  
                    WHERE 
                        A.SEQ_KEY = {SEQ_KEY} AND 
                        A.ORDEM = {ORDEM} 
                        
                """
        engine = self.cria_Conn()
        if engine:
            df = pd.read_sql(query, engine)
            engine.dispose()
            return df
        else:
            return None



    def avalia_faixas_aprovacao(self, SEQ_KEY, ORDEM, predict):
        sql = f"""        
            SELECT     
                    Acao = MAX(FAIXAS.Ação),
                    ORDEM = VALORES.ORDEM,
                    FAIXAS.Outcome,
                    Descriçao_Ação = (SELECT TOP 1 DESCFAIXAS.Descriçao_Ação FROM {self.schema_main}.FNML481L DESCFAIXAS WHERE MAX(FAIXAS.Ação) = DESCFAIXAS.Ação),
                    VARIACAO_IMXIC        = MAX(ABS(VALORES.VARIACAO_IMXIC)),    
                    LIMITE_VARIACAO_IMXIC = LIMITE.VARIACAO_IMXIC,
                    DIF_CUSTO_P_x_R        = MAX(ABS(VALORES.DIF_CUSTO_P_x_R)) ,
                    LIMITE_DIF_CUSTO_P_x_R = LIMITE.DIF_CUSTO_P_x_R,
                    MAT_DIF_PERCENTUAL    = MAX(ABS(VALORES.MAT_DIF_PERCENTUAL)), 
                    LIMITE_MAT_DIF_PERCENTUAL = LIMITE.MAT_DIF_PERCENTUAL,
                    TAXA_MAQUINA_FIXA    = MAX(ABS(VALORES.TAXA_MAQUINA_FIXA)),
                    LIMITE_TAXA_MAQUINA_FIXA = LIMITE.TAXA_MAQUINA_FIXA,
                    TAXA_MO_FIXA        = MAX(ABS(VALORES.TAXA_MO_FIXA)),
                    LIMITE_TAXA_MO_FIXA = LIMITE.TAXA_MO_FIXA,
                    TAXA_FIXA_VAR_MO    = MAX(ABS(VALORES.TAXA_FIXA_VAR_MO)),
                    LIMITE_TAXA_FIXA_VAR_MO = LIMITE.TAXA_FIXA_VAR_MO,
                    MO_VALOR            = MAX(ABS(VALORES.MO_VALOR)),
                    LIMITE_MO_VALOR = LIMITE.MO_VALOR,
                    HR_MAQ_VALOR        = MAX(ABS(VALORES.HR_MAQ_VALOR)),
                    LIMITE_HR_MAQ_VALOR = LIMITE.HR_MAQ_VALOR,
                    HR_EXC_VLR            = MAX(ABS(VALORES.HR_EXC_VLR)),    
                    LIMITE_HR_EXC_VLR = LIMITE.HR_EXC_VLR,
                    HR_CONFIG_VLR        = MAX(ABS(VALORES.HR_CONFIG_VLR)),    
                    LIMITE_HR_CONFIG_VLR = LIMITE.HR_CONFIG_VLR,
                    MO_VARIACAO            = MAX(ABS(VALORES.MO_VARIACAO)),
                    LIMITE_MO_VARIACAO = LIMITE.MO_VARIACAO,
                    EXTERNA_OPERACAO    = MAX(ABS(VALORES.EXTERNA_OPERACAO)),
                    LIMITE_EXTERNA_OPERACAO = LIMITE.EXTERNA_OPERACAO,
                    VAR_EM_REAIS        = MAX(ABS(VALORES.VAR_EM_REAIS)),
                    LIMITE_VAR_EM_REAIS = LIMITE.VAR_EM_REAIS 
                FROM  
                        {self.schema_main}.FNML481 VALORES,
                        {self.schema_main}.FNML481L FAIXAS
                        LEFT JOIN 
                        {self.schema_main}.FNML481L LIMITE ON
                        LIMITE.AÇÃO IN ('1','3') AND
                        LIMITE.Outcome = FAIXAS.Outcome

                WHERE
                    (
                    ABS(VALORES.VARIACAO_IMXIC)         >    FAIXAS.VARIACAO_IMXIC OR 
                    ABS(VALORES.DIF_CUSTO_P_x_R)        >    FAIXAS.DIF_CUSTO_P_x_R OR
                    ABS(VALORES.MAT_DIF_PERCENTUAL)     >    FAIXAS.MAT_DIF_PERCENTUAL OR
                    ABS(VALORES.TAXA_MAQUINA_FIXA)      >    FAIXAS.TAXA_MAQUINA_FIXA OR
                    ABS(VALORES.TAXA_MO_FIXA)           >    FAIXAS.TAXA_MO_FIXA OR
                    ABS(VALORES.TAXA_FIXA_VAR_MO)       >    FAIXAS.TAXA_FIXA_VAR_MO OR
                    ABS(VALORES.MO_VALOR)               >    FAIXAS.MO_VALOR OR
                    ABS(VALORES.HR_MAQ_VALOR)           >    FAIXAS.HR_MAQ_VALOR OR
                    ABS(VALORES.HR_EXC_VLR)             >    FAIXAS.HR_EXC_VLR OR
                    ABS(VALORES.HR_CONFIG_VLR)          >    FAIXAS.HR_CONFIG_VLR OR
                    ABS(VALORES.MO_VARIACAO)            >    FAIXAS.MO_VARIACAO OR
                    ABS(VALORES.EXTERNA_OPERACAO)       >    FAIXAS.EXTERNA_OPERACAO OR
                    ABS(VALORES.VAR_EM_REAIS)           >    FAIXAS.VAR_EM_REAIS
                    )
                    AND  VALORES.SEQ_KEY = {SEQ_KEY} 
                    AND  VALORES.ORDEM = {ORDEM}
                    AND  FAIXAS.Outcome = '{predict}'       
                GROUP BY 
                     FAIXAS.Outcome,
                     VALORES.ORDEM,
                     LIMITE.VARIACAO_IMXIC,
                     LIMITE.DIF_CUSTO_P_x_R,
                     LIMITE.MAT_DIF_PERCENTUAL,
                     LIMITE.TAXA_MAQUINA_FIXA,
                     LIMITE.TAXA_MO_FIXA,
                     LIMITE.TAXA_FIXA_VAR_MO,
                     LIMITE.MO_VALOR,
                     LIMITE.HR_MAQ_VALOR,
                     LIMITE.HR_EXC_VLR,
                     LIMITE.HR_CONFIG_VLR,
                     LIMITE.MO_VARIACAO,
                     LIMITE.EXTERNA_OPERACAO,
                     LIMITE.VAR_EM_REAIS               
            """
        engine = self.cria_Conn()
        if engine:
            df = pd.read_sql(sql, engine)
            engine.dispose()
            return df
        else:
            return None


    def json_avalia_faixas_aprovacao(self, SEQ_KEY, ordem, predict):
        df = self.avalia_faixas_aprovacao(SEQ_KEY, ordem, predict)
        if df is not None:
            # Cria uma lista de dicionários para cada linha, sinalizando valores superiores aos limites
            results = []
            for index, row in df.iterrows():
                result = {col: row[col] for col in df.columns}
                for col in df.columns:
                    if "LIMITE_" in col and col.replace("LIMITE_", "") in df.columns:
                        value_col = col.replace("LIMITE_", "")
                        result[f"{value_col}_EXCEDE_LIMITE"] = row[value_col] > row[col]
                results.append(result)

            # Converte a lista de resultados em JSON
            json_result = json.dumps(results, ensure_ascii=False, indent=4)

            return json_result
        else:
            return None


    def preprocess_data(self, df):
        # Remover as colunas identificadoras
        identifiers = df[['SEQ_KEY', 'ORDEM']]
        df = df.drop(['SEQ_KEY', 'ORDEM'], axis=1)

        # Aplicar a codificação dummies (se necessário)
        df = pd.get_dummies(df)

        # Carregar o scaler treinado
        scaler_path = os.path.join(self.root_path, 'scaler.joblib')
        scaler = joblib.load(scaler_path)
        df_normalized = scaler.transform(df)

        return df_normalized, identifiers

    def classificar_ordem(self, df):
        # Carregar o modelo treinado
        model_path = os.path.join(self.root_path, 'best_random_forest_model.joblib')
        model = joblib.load(model_path)

        # Pré-processar os dados
        df_normalized, identifiers = self.preprocess_data(df)

        # Realizar a classificação
        predictions = model.predict(df_normalized)

        # Adicionar as previsões ao DataFrame original
        df['Predicted_OUTCOME'] = predictions

        # Restaurar os identificadores
        result_df = pd.concat([identifiers.reset_index(drop=True), df.reset_index(drop=True)], axis=1)

        return result_df
