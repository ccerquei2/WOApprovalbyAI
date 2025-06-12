import time
from crewai import Crew
from agents import ProductionOrderAgents, VariationReviewerAgents, CostDecisionAgents, CostVariationReviewerAgents, BaseAgent
from tasks import AnalyzeVariationTask, ReviewVariationTask, Cost_AnalyzeVariationTask, CostReviewVariationTask
from datetime import datetime
import pyodbc
import re
from dotenv import load_dotenv
load_dotenv()

import os
import sys
import joblib
import json
import concurrent.futures
import signal
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from load_environment import ConfigLoader
from decrypt import decrypt_keys
from aiwo_logger import db_logged

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="__init__")

def load_prompts():
    if hasattr(sys, '_MEIPASS'):
        # Estamos em um executável PyInstaller
        base_path = sys._MEIPASS
    else:
        # Estamos em um ambiente de desenvolvimento
        base_path = os.path.abspath(os.path.dirname(__file__))

    translation_path = os.path.join(base_path, 'crewai', 'translations', 'en.json')

    with open(translation_path, 'r') as file:
        prompts = json.load(file)
    return prompts

def load_model():
    if hasattr(sys, '_MEIPASS'):
        # Estamos em um executável PyInstaller
        model_path = os.path.join(sys._MEIPASS, 'best_random_forest_model.joblib')
    else:
        # Estamos em um ambiente de desenvolvimento
        # model_path = 'C:/Users/ccerq/OneDrive/Documentos/Python Scripts/ML_CostAnalysis/best_random_forest_model.joblib'
        model_path = 'C:/Users/ccerq/OneDrive/Documentos/Python Scripts/ML_CostAnalysis3/best_random_forest_model.joblib'

    model = joblib.load(model_path)
    return model

# Exemplo de como usar as funções
prompts1 = load_prompts()
model1 = load_model()



class PipeLineCoastJustify:

    def __init__(self, environment='dev', logger=None, execution_id=None):
        
        config_loader = ConfigLoader(environment)
        db_config = config_loader.get_database_config()
        self.server = db_config['server']
        self.database = db_config['database']
        self.username = decrypt_keys("username")
        self.password = decrypt_keys("password")
        self.schema_main = db_config['schema_main']
        self.schema_udc = db_config['schema_udc']
        self.root_path = os.path.dirname(os.path.abspath(__file__))
        self.logger = logger
        self.execution_id = execution_id

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



    def julian_date(self, date):
        """ Converte uma data em formato padrão para o formato Julian Date."""
        year = date.year % 100  # Obtém os dois últimos dígitos do ano
        day_of_year = (date - datetime(date.year, 1, 1)).days + 1
        return f"1{year:02d}{day_of_year:03d}"

    @db_logged(step="InsertApprovalResult", phase="Post-action")
    def insert_approval_result(self, seq_key, ordem, decisao_aprovar, agent_return, json_avalia_limites_str,
                               approval_decision, what_llm, groq_model=None):

        user_uid = decrypt_keys("user_uid")
        pass_pwd = decrypt_keys("password_pwd")

        conn_str = (
            f"DRIVER={{SQL Server}};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"UID={user_uid};"
            f"PWD={pass_pwd}"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()


        # Obter o próximo valor para GFN002
        cursor.execute(f"""
            SELECT ISNULL(MAX(GFN002), 0) + 1
            FROM  {self.schema_main}.FN31112Z
            WHERE GFDOCO = ?
        """, ordem)
        gfn002 = cursor.fetchone()[0]

        # Obter a data e hora atuais
        now = datetime.now()
        julian_now = self.julian_date(now)
        gftday = now.strftime("%H%M%S")

        if groq_model == None: groq_model = ''

        # Inserir os dados na tabela
        cursor.execute(f"""
            INSERT INTO  {self.schema_main}.FN31112Z (
                GFN001, GFDOCO, GFN002, GFN003, GFDES1, GFNOTTE, GFANSR,
                GFURCD, GFURDT, GFURRF, GFURAT, GFURAB, GFCFGD, GFUSER,
                GFPID, GFUPMJ, GFTDAY
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, seq_key, ordem, gfn002, decisao_aprovar, approval_decision, agent_return, json_avalia_limites_str,
                       what_llm, 0, groq_model, 0, 0, julian_now, 'AIAGENT1', 'PYTHONAI1', julian_now, gftday)

        # Confirmar a transação
        conn.commit()

        # Fechar a conexão
        cursor.close()
        conn.close()






    def approval_decision_qtd(self, df_qtd, justify, acao, what_llm, limits_return, groq_model=None):
        # time.sleep(6)
        # Criação dos agentes

        if groq_model == None:
            model1 = BaseAgent()
        else:
            model1 = BaseAgent(groq_model)

        available_models = model1.choice_llms()

        agents = ProductionOrderAgents()
        reviewer_agents = VariationReviewerAgents()


        variation_analyzer = agents.variation_analysis_agent(available_models[what_llm])
        variation_reviewer = reviewer_agents.variation_reviewer_agent(available_models[what_llm])
        print("llma usada foi:", what_llm)

        tasks = AnalyzeVariationTask()
        review_tasks = ReviewVariationTask()

        analyze_variation_tasks = []
        review_variation_tasks = []

        order_details_qtd = {

            'Variação_Quantidade': float(df_qtd['Variação_Quantidade'].iloc[0]),
            'Variação_Valor_Total_Quantidade': float(df_qtd['Variação_Valor_Total_Quantidade'].iloc[0]),
            'Diferença_Hora_Maquina': float(df_qtd['Diferença_Hora_Maquina'].iloc[0]),
            'Diferença_Hora_Execução': float(df_qtd['Diferença_Hora_Execução'].iloc[0]),
            'Diferença_Hora_Configuração': float(df_qtd['Diferença_Hora_Configuração'].iloc[0]),
            'Variação_Valor_Total_Horas': float(df_qtd['Variação_Valor_Total_Horas'].iloc[0]),
            'Factory_Justify': justify
        }

        # Criação da tarefa de análise de variação
        analyze_task = tasks.analyze_variation_qtd(
            agent=variation_analyzer,
            order_details_qtd=order_details_qtd
        )

        # Adiciona a tarefa de análise ao crew
        analyze_variation_tasks.append(analyze_task)

        # Executa a análise de variação e obtém a decisão
        crew = Crew(
            agents=[variation_analyzer],
            tasks=analyze_variation_tasks,
            max_rpm=29
        )

        start_time = time.time()
        results = crew.kickoff()
        # results = self.execute_with_retries(crew)

        end_time = time.time()
        elapsed_time = end_time - start_time

        print(f"Crew kickoff took {elapsed_time} seconds.")
        print("Crew usage", crew.usage_metrics)

        # print("Resultado da Analise do Primeiro Agente:", results)

        # Criação da tarefa de análise de variação
        analyze_task = review_tasks.review_variation(
            agent=variation_reviewer,
            approval_decision=results,
            order_details_qtd=order_details_qtd
        )

        # Adiciona a tarefa de análise ao crew
        review_variation_tasks.append(analyze_task)

        # Adiciona a tarefa de revisão ao crew
        crew = Crew(
            agents=[variation_reviewer],
            tasks=review_variation_tasks,
            max_rpm=29
        )

        time.sleep(5)
        start_time = time.time()
        # review_results = self.execute_with_retries(crew)
        results = crew.kickoff()
        end_time = time.time()
        elapsed_time = end_time - start_time

        # Usando expressão regular para extrair a decisão de validação
        match = re.search(r"Decisão de Validação: (Validado|Não Validado)", results)
        if match:
            decisao_aprovar = match.group(0)
            # print("Decisão de Aprovação:", decisao_aprovar)
        else:
            decisao_aprovar = "Decisão de Validação: Não Validado"

        Justify_and_AgentReturn =  results + '\n\n\nJustificativa feita pela Fabrica: ' + justify

        # Avoid insert error
        if groq_model == None:
            truncated_model_name = 'Standard Model'
        else:
            truncated_model_name = groq_model[:15] if len(groq_model) > 15 else groq_model


        self.insert_approval_result(float(df_qtd['Seq_Key'].iloc[0]),
                                    float(df_qtd['Ordem'].iloc[0]),
                                    acao,
                                    Justify_and_AgentReturn,
                                    limits_return,
                                    decisao_aprovar,
                                    what_llm,
                                    truncated_model_name)


        print("Resultado da Analise do Segundo Agente:", results)
        print("Decisão de Aprovação:", decisao_aprovar)

        print("Resultado da Analise do Segundo Agente:", results)

        print(f"Review crew kickoff took {elapsed_time} seconds.")
        print("Review crew usage", crew.usage_metrics)

        return results, decisao_aprovar



    def cost_approval_decision2(self, df, acao, what_llm, limits_return,groq_model=None):
        # Criação dos agentes
        model1 = BaseAgent()
        available_models = model1.choice_llms()

        agents = CostDecisionAgents()
        reviewer_agents = CostVariationReviewerAgents()

        variation_analyzer = agents.cost_variation_analysis_agent(available_models[what_llm])
        variation_reviewer = reviewer_agents.cost_variation_reviewer_agent(available_models[what_llm])
        print("llma usada foi:", what_llm)

        tasks = Cost_AnalyzeVariationTask()
        review_tasks = CostReviewVariationTask()

        analyze_variation_tasks = []
        review_variation_tasks = []

        order_details = {
            'Material_Used': float(df['MAT_DIF_PERCENTUAL'].iloc[0]),
            'Setup_Hours': float(df['HR_CONFIG_VLR'].iloc[0]),
            'Labor_Hours': float(df['MO_VALOR'].iloc[0]),
            'Machine_Hours': float(df['HR_MAQ_VALOR'].iloc[0]),
            'External_Operation': float(df['EXTERNA_OPERACAO'].iloc[0]),
            'Standard_x_Real': float(df['DIF_CUSTO_P_x_R'].iloc[0]),
            'Variation_IMxIC': float(df['VARIACAO_IMXIC'].iloc[0]),
            'Variation_Material': float(df['MAT_DIF_PERCENTUAL'].iloc[0]),
            'Rate_Machine': float(df['TAXA_MAQUINA_FIXA'].iloc[0]),
            'Rate_Labor': float(df['TAXA_MO_FIXA'].iloc[0]),
            'Rate_Var_Labor': float(df['TAXA_FIXA_VAR_MO'].iloc[0]),
            'Predicted_OUTCOME': df['Predicted_OUTCOME'].iloc[0]
        }

        # Criação da tarefa de análise de variação
        analyze_task = tasks.costanalyze_variation(
            agent=variation_analyzer,
            order_details=order_details
        )

        # Adiciona a tarefa de análise ao crew
        analyze_variation_tasks.append(analyze_task)

        # Executa a análise de variação e obtém a decisão
        crew = Crew(
            agents=[variation_analyzer],
            tasks=analyze_variation_tasks,
            max_rpm=29
        )

        start_time = time.time()
        results = crew.kickoff()
        # results = self.execute_with_retries(crew)
        end_time = time.time()
        elapsed_time = end_time - start_time

        print(f"Crew kickoff took {elapsed_time} seconds.")
        print("Crew usage", crew.usage_metrics)

        print("Resultado da Analise do Primeiro Agente:", results)

        # Criação da tarefa de análise de variação
        analyze_task = review_tasks.cost_review_variation(
            agent=variation_reviewer,
            approval_decision=results,
            order_details=order_details
        )

        # Adiciona a tarefa de análise ao crew
        review_variation_tasks.append(analyze_task)

        # Adiciona a tarefa de revisão ao crew
        crew = Crew(
            agents=[variation_reviewer],
            tasks=review_variation_tasks,
            max_rpm=29
        )

        time.sleep(5)
        start_time = time.time()
        results = crew.kickoff()
        # review_results = self.execute_with_retries(crew)
        end_time = time.time()
        elapsed_time = end_time - start_time


        # Usando expressão regular para extrair a decisão de validação
        match = re.search(r"Decisão de Validação: (Validado|Não Validado)", results)
        if match:
            decisao_aprovar = match.group(0)
            # print("Decisão de Aprovação:", decisao_aprovar)
        else:
            decisao_aprovar = "Decisão de Validação: Não Validado"

        # Avoid insert error
        if groq_model == None:
            truncated_model_name = 'Standard Model'
        else:
            truncated_model_name = groq_model[:15] if len(groq_model) > 15 else groq_model

        self.insert_approval_result(float(df['SEQ_KEY'].iloc[0]),
                                    float(df['ORDEM'].iloc[0]),
                                    acao,
                                    results,
                                    limits_return,
                                    decisao_aprovar,
                                    what_llm,
                                    truncated_model_name)

        print("Resultado da Analise do Segundo Agente:", results)

        print(f"Review crew kickoff took {elapsed_time} seconds.")
        print("Review crew usage", crew.usage_metrics)

        return results, decisao_aprovar



    def execute_with_retries2(self, df, justify, acao, limits_return, groqmodel=None, max_retries=3, max_time=120):
        def try_llm(llm, retries):
            attempts = 0
            while attempts < retries:
                start_time = time.time()  # Reinicia o tempo de início a cada tentativa
                try:
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        if acao == 0:
                            # future = executor.submit(self.approval_decision2, df, justify, acao, llm, limits_return, groqmodel)
                            future = executor.submit(self.approval_decision_qtd, df, justify, acao, llm, limits_return, groqmodel)
                            result = future.result(timeout=max_time)  # Cada tentativa tem o tempo total disponível

                        if acao == 2 or acao == -2:
                            # future = self.cost_approval_decision2(df, acao, llm, limits_return, groqmodel)
                            future = executor.submit(self.cost_approval_decision2, df, acao, llm, limits_return, groqmodel)
                            result = future.result(timeout=max_time)  # Cada tentativa tem o tempo total disponível

                    return result, future._result[1]  # Sucesso
                except concurrent.futures.TimeoutError:
                    print(f"Timeout ocorrido com LLM {llm}. Tentativa {attempts + 1}/{retries}.")
                except Exception as e:
                    print(f"Erro encontrado com LLM {llm}: {e}. Tentativa {attempts + 1}/{retries}.")
                finally:

                    executor.shutdown(wait=True)  # Garante que as threads sejam finalizadas
                    attempts += 1

            # Se todas as tentativas falharem, retorna None
            return None

        def handle_llm_attempt(llm, llm_name, retries):
            result = None
            try:
                with db_logged(step=f"{llm_name}Call", phase="Inference", api_name=llm_name,
                               logger=self.logger, execution_id=self.execution_id):
                    result = try_llm(llm, retries)
                    if result is None:
                        raise RuntimeError(f"{llm_name} failed after all retries")
            except Exception:
                print(f"Falha com {llm_name} após todas as tentativas.")
                return None
            else:
                print(f"Resultado da Análise com {llm_name}:", result)
                return result

        try:
            # Tenta o Groq primeiro
            result = handle_llm_attempt(llm=0, llm_name="Groq", retries=max_retries)
            if result is not None:
                return result

            # Tenta a contingência (OpenAI) após falhar com o Groq
            result = handle_llm_attempt(llm=1, llm_name="OpenAI", retries=max_retries)
            if result is not None:
                return result

            # Se falhar tanto com Groq quanto com OpenAI
            print("Falha total: Nenhuma LLM conseguiu completar a tarefa após todas as tentativas.")
            if self.logger:
                self.logger.log(
                    level="ERROR",
                    step="LLMCall",
                    execution_id=self.execution_id,
                    phase="Inference",
                    message="Both LLMs failed"
                )
            return None

        finally:
            print("Processo finalizado.") # Comando " os._exit(1) " foi movido para o arquivo main apos execução de execute_with_retries2
            # os._exit(1)  # Encerra o programa de forma abrupta //


