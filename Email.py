import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
import pandas as pd
import re
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from load_environment import ConfigLoader



class PrepareEmail:

    def __init__(self, environment='dev'):
        config_loader = ConfigLoader(environment)
        db_config = config_loader.get_database_config()
        self.server = db_config['server']
        self.database = db_config['database']
        self.username = 'consultas_diretas'
        self.password = 'c_diretas'
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


    def destinatarios_email(self):
        query = f"""
                SELECT DRDL01
                FROM
                    {self.schema_udc}.F0005 WITH (NOLOCK)
                WHERE
                    DRSY = '58' AND
                    DRRT = 'E5'
                """

        engine = self.cria_Conn()
        if engine:
            df_email_list = pd.read_sql(query, engine)

            # Process the emails
            email_series = df_email_list['DRDL01'].dropna()
            email_list = []
            for item in email_series:
                # Split emails by commas or semicolons
                emails = [email.strip() for email in re.split(r'[;,]', item)]
                email_list.extend(emails)
            # Remove duplicates
            email_list = list(set(email_list))
            # Convert the list to a string
            email_string = '; '.join(email_list)
            return email_string
        else:
            return ''


    def create_report_html(self, df_qtd, json_avalia_limites, tipo_email):
        # Extrair dados de df_qtd
        ordem = df_qtd['Ordem'].iloc[0]
        var_quantidade = df_qtd['Variação_Quantidade'].iloc[0]
        var_valor_total_quantidade = df_qtd['Variação_Valor_Total_Quantidade'].iloc[0]
        dif_hora_maquina = df_qtd['Diferença_Hora_Maquina'].iloc[0]
        dif_hora_execucao = df_qtd['Diferença_Hora_Execução'].iloc[0]
        dif_hora_configuracao = df_qtd['Diferença_Hora_Configuração'].iloc[0]
        var_valor_total_horas = df_qtd['Variação_Valor_Total_Horas'].iloc[0]

        # Obter o ano atual
        current_year = datetime.datetime.now().year

        # Função auxiliar para formatar números com vírgulas
        def format_number(num):
            return f"{num:.2f}".replace('.', ',')

        exceeded_limits = []
        if tipo_email == 'erro_faixas':
            # Preparar a lista de limites excedidos de json_avalia_limites
            parameter_mapping = {
                'VARIACAO_IMXIC': 'Variação IMXIC',
                'DIF_CUSTO_P_x_R': 'Diferença de Custo Padrão x Real',
                'MAT_DIF_PERCENTUAL': 'Diferença Percentual de Material',
                'TAXA_MAQUINA_FIXA': 'Taxa Máquina Fixa',
                'TAXA_MO_FIXA': 'Taxa Mão de Obra Fixa',
                'TAXA_FIXA_VAR_MO': 'Taxa Fixa Variável Mão de Obra',
                'MO_VALOR': 'Mão de Obra Valor',
                'HR_MAQ_VALOR': 'Hora Máquina',
                'HR_EXC_VLR': 'Hora Execução Valor',
                'HR_CONFIG_VLR': 'Hora Configuração Valor',
                'MO_VARIACAO': 'Mão de Obra Variação',
                'EXTERNA_OPERACAO': 'Operação Externa',
                'VAR_EM_REAIS': 'Variação em Reais'
            }

            for entry in json_avalia_limites:
                for key, value in entry.items():
                    if key.endswith('_EXCEDE_LIMITE') and value == True:
                        param_code = key[:-len('_EXCEDE_LIMITE')]
                        param_value = entry.get(param_code)
                        limit_key = 'LIMITE_' + param_code
                        param_limit = entry.get(limit_key)
                        param_name = parameter_mapping.get(param_code, param_code)
                        param_value_str = format_number(param_value)
                        param_limit_str = format_number(param_limit)
                        if param_name == 'Variação em Reais':
                            line = f"{param_name} em {param_value_str} que ultrapassou o limite de {param_limit_str}"
                        else:
                            line = f"{param_name} em {param_value_str}% que ultrapassou o limite de {param_limit_str}%."
                        exceeded_limits.append(line)

        # Definir a cor com base no tipo de email
        if tipo_email == 'erro_faixas':
            frame_color = '#0d6efd'  # Azul
            title_box = 'Notificação de Variações'
        else:
            frame_color = '#197047'  # Verde
            title_box = 'Necessidade de Justificativa da Fabrica'

        # Gerar o HTML para os limites excedidos
        if exceeded_limits:
            exceeded_limits_html = ""
            for line in exceeded_limits:
                exceeded_limits_html += f"<li style='margin-bottom:5px;'>{line}</li>\n"
            # Construir a seção de limites extrapolados
            limites_extrapolados_section = f"""
            <!-- Seção de Limites Extrapolados -->
            <tr>
                <td style="padding: 20px; font-size: 16px; line-height: 1.5; color: #555555;">
                    <h2 style="font-size: 20px; color: #333333;">Faixas de Tolerância Extrapoladas</h2>
                    <p>
                        As faixas de tolerância para aprovação via agentes inteligentes foram extrapoladas em:
                    </p>
                    <ul style="padding-left: 20px; margin: 0;">
                        {exceeded_limits_html}
                    </ul>
                </td>
            </tr>
            """
        else:
            limites_extrapolados_section = ""

        # Template HTML com placeholders e cores dinâmicas
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{title_box}</title>
        </head>
        <body style="margin:0; padding:0; font-family: Arial, sans-serif; background-color: #f6f6f6;">
            <table width="100%" bgcolor="#f6f6f6" cellpadding="0" cellspacing="0" border="0">
                <tr>
                    <td align="center">
                        <table width="600" bgcolor="#ffffff" cellpadding="0" cellspacing="0" border="0" style="border-collapse: collapse;">
                            <!-- Cabeçalho -->
                            <tr>
                                <td align="center" bgcolor="{frame_color}" style="padding: 20px;">
                                    <h1 style="color: #ffffff; font-size: 24px; margin: 0;">{title_box}</h1>
                                </td>
                            </tr>
                            <!-- Seção de Variações -->
                            <tr>
                                <td style="padding: 20px; font-size: 16px; line-height: 1.5; color: #555555;">
                                    <h2 style="font-size: 20px; color: #333333;">Variações de Quantidades da Ordem <span style="color: #ff0000;">{int(ordem)}</span></h2>
                                    <p>
                                        <strong>Percentual total de Quantidade Retirada (Real - Padrão):</strong> {format_number(var_quantidade)}%<br>
                                        A variação acima afetou o custo da ordem em {format_number(var_valor_total_quantidade)}%.
                                    </p>
                                </td>
                            </tr>
                            <!-- Seção de Diferenças de Horas -->
                            <tr>
                                <td style="padding: 20px; font-size: 16px; line-height: 1.5; color: #555555;">
                                    <h2 style="font-size: 20px; color: #333333;">Diferenças de Quantidade de Horas (Real - Padrão)</h2>
                                    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-collapse: collapse; margin-top: 15px;">
                                        <tr>
                                            <th align="left" bgcolor="#f2f2f2" style="border: 1px solid #dddddd; padding: 10px;">Tipo</th>
                                            <th align="left" bgcolor="#f2f2f2" style="border: 1px solid #dddddd; padding: 10px;">Variação </th>
                                        </tr>
                                        <tr>
                                            <td style="border: 1px solid #dddddd; padding: 10px;">Máquina</td>
                                            <td style="border: 1px solid #dddddd; padding: 10px;">{format_number(dif_hora_maquina)}</td>
                                        </tr>
                                        <tr>
                                            <td style="border: 1px solid #dddddd; padding: 10px;">Execução</td>
                                            <td style="border: 1px solid #dddddd; padding: 10px;">{format_number(dif_hora_execucao)}</td>
                                        </tr>
                                        <tr>
                                            <td style="border: 1px solid #dddddd; padding: 10px;">Configuração</td>
                                            <td style="border: 1px solid #dddddd; padding: 10px;">{format_number(dif_hora_configuracao)}</td>
                                        </tr>
                                    </table>
                                    <p>
                                        O somatório das diferenças de horas afetou o custo da ordem em {format_number(var_valor_total_horas)}%.
                                    </p>
                                </td>
                            </tr>
                            {limites_extrapolados_section}
                            <!-- Rodapé -->
                            <tr>
                                <td align="center" bgcolor="{frame_color}" style="padding: 15px; font-size: 14px; color: #ffffff;">
                                    &copy; {current_year} Casa Granado|Phebo. Todos os direitos reservados.
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        return html_template


    def send_email(self, subject, body, to_addr, from_addr):
        # Configuração do servidor SMTP do Outlook
        # smtp_server = 'smtp.office365.com'
        # smtp_port = 587

        lista_destinatarios = self.destinatarios_email()
        to_addr = lista_destinatarios

        if to_addr == '' or to_addr == []:
            to_addr = "ccerqueira@granadophebo.com.br"

        smtp_server = 'wsus.granado.com.br'
        smtp_port = 25

        # Criando uma mensagem Multipart
        msg = MIMEMultipart()
        msg['From'] = from_addr
        msg['To'] = to_addr
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        # Conectando ao servidor SMTP e enviando o e-mail
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # Ativa a encriptação TLS
            # server.login(from_addr, password)  # login no servidor
            server.send_message(msg)  # Envia a mensagem criada
            server.quit()
            print("E-mail enviado com sucesso!")
        except Exception as e:
            print("Falha ao enviar e-mail:", e)


