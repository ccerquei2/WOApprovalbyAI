
from zeep import Client
from zeep import Settings
from zeep.wsse.username import UsernameToken
from zeep.transports import Transport
import requests
import pyodbc
import pandas as pd
from load_environment import ConfigLoader
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import os
from decrypt import decrypt_keys

class ApproveWorkOrder:

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

        conn_str = f'DRIVER={{SQL Server}};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}'
        try:
            conn = pyodbc.connect(conn_str)
            return conn
        except Exception as e:
            print("Error to connect to the database:", e)
            return None



    def extrair_dados(self):
        query = f"""
                SELECT DRSPHD 
                FROM  
                    {self.schema_udc}.F0005  WITH(NOLOCK)  
                WHERE  
                    DRSY = '58'  AND
                    DRRT = '8A'  AND  
                    DRKY = 'BSSV_ONOFF'
                """
        conn = self.cria_Conn()
        if conn:
            df_bssv_approval = pd.read_sql(query, conn)
            conn.close()
            return df_bssv_approval
        else:
            return None


    def ApproveOrderJDE(self, environment, order):

        try:

            verify_approval_status = self.extrair_dados()

            if verify_approval_status['DRSPHD'].iloc[0].rstrip() == 'Y':

                # Configurar a sessão para ignorar a verificação SSL (se necessário)
                session = requests.Session()
                session.verify = False  # Desabilita a verificação SSL

                transport = Transport(session=session)

                if environment == 'prod':    # URL do WSDL
                    wsdl = 'https://bssvsistemas.granado.com.br:9061/PD910/CustomContabilizaOrdens?wsdl'
                else:
                    wsdl = 'https://weberp06.granado.com.br:9052/PY910/CustomContabilizaOrdens?wsdl'


                # Credenciais

                username = decrypt_keys("user_bssv")
                password = decrypt_keys("password_bssv")

                # Criar o cliente SOAP com autenticação WS-Security
                client = Client(wsdl=wsdl, wsse=UsernameToken(username, password), transport=transport)

                # Parâmetros da chamada
                chave_ordem = int(order)
                version = 'CGRA0001J'

                # Realizar a chamada ao serviço
                try:
                    response = client.service.ContabilizaOrdens(ordem=chave_ordem, version=version)
                    # print(response)
                    return "Submissão de aprovação da ordem " + str(int(order)) + " foi finalizada com sucesso."

                except Exception as e2:
                    print(f"Ocorreu um erro: {e2}")

            else:
                print('Execução da aprovação via BSSV desligado na UDC 58/8A')

        except Exception as e1:
            print(f"Ocorreu um erro: {e1}")


