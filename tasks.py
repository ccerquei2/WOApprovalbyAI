

from crewai import Task

class AnalyzeVariationTask():

    def analyze_variation_qtd(self, agent, order_details_qtd):
        return Task(
            description=f"""
                  Analise a justificativa fornecida em relação à variação e decida sobre a aprovação.

                  Detalhes das Variações relacionadas a Quantidades de Material e Quantidades de Horas:
                  
                  - 'Variação de Quantidade': {order_details_qtd['Variação_Quantidade']}%
                  - 'Diferença Hora Maquina': {order_details_qtd['Diferença_Hora_Maquina']}
                  - 'Diferença Hora Execução': {order_details_qtd['Diferença_Hora_Execução']}
                  - 'Diferença Hora Configuração': {order_details_qtd['Diferença_Hora_Configuração']}
                  - Justificativa da Fábrica: '{order_details_qtd['Factory_Justify']}'

                  Diretrizes:
                  - Analisar se a justificativa da Fábrica explica as variações observadas. 
                    Caso a justificativa aborde as variações a ordem poderá se aprovada caso a justificativa não abordem 
                    as variações a ordem não deverá ser aprovada.                 

              """,
            agent=agent,
            expected_output="Forneça uma decisão de aprovação ou rejeição com justificativas claras para cada variação "
                            "analisada. ",
            async_execution=False,
        )

    def analyze_variation(self, agent, order_details):
        return Task(
            description=f"""
                Analise a justificativa fornecida em relação à variação e decida sobre a aprovação.

                Detalhes da Ordem e Variações Percentuais:
                - 'Material Utilizado': {order_details['Material_Used']}%
                - 'Horas de Setup': {order_details['Setup_Hours']}%
                - 'Horas de Trabalho': {order_details['Labor_Hours']}%
                - 'Horas de Máquina': {order_details['Machine_Hours']}%
                - 'Operação Externa': {order_details['External_Operation']}%
                - 'Padrão x Real': {order_details['Standard_x_Real']}%
                - 'Variação IM x IC': {order_details['Variation_IMxIC']}%
                - 'Variação de Material': {order_details['Variation_Material']}%
                - 'Taxa de Máquina': {order_details['Rate_Machine']}%
                - 'Taxa de Trabalho': {order_details['Rate_Labor']}%
                - 'Taxa de Variação do Trabalho': {order_details['Rate_Var_Labor']}%
                - Ação Prevista pelo Agente: {order_details['Predicted_OUTCOME']}

                - Justificativa da Fábrica: '{order_details['Factory_Justify']}'

                Diretrizes:
                - 'Variação IM x IC' maior que 0,02 então Não aprovar, mas se 'Variação IM x IC' for menor que
                0,02 avaliar demais parametros de custo para decidir sobre a aprovação.
                - Ação Prevista como 'REQUER JUSTIFICATIVA FABRICA': Requer justificativa detalhada.
                - Ação Prevista como 'APROVADO COM JUSTIFICATIVA SETOR CUSTOS': Aprovar a ordem com comentários sobre
                os valores.

            """,
            agent=agent,
            expected_output="Forneça uma decisão de aprovação ou rejeição com justificativas claras para cada variação "
                            "analisada.",
            async_execution=False,
        )


class ReviewVariationTask():
    def review_variation(self, agent, approval_decision, order_details_qtd):
        return Task(
            description=f"""
                Revise a decisão de aprovação e a justificativa fornecida para garantir precisão e relevância.

                Decisão de Aprovação:
                {approval_decision}
                Variações Percentuais da Ordem:
                -  Valores Negativos igual a melhor rentabilidade
                -  Valores Positivos igual a custo acima do esperado
                {order_details_qtd}

                Diretrizes:
                - Verifique se a justificativa é relevante e apropriada para a variação observada.
                - Emita uma decisão de validação com base na revisão da decisão do analista.
              
                Formato de resposta esperado:
                - Decisão de Validação: [Validado/Não Validado]
                - Motivo da Decisão: [Explique brevemente a base de sua decisão, focando na relevância e adequação da
                justificativa fornecida].
            """,
            agent=agent,
            expected_output="Forneça uma decisão de validação com justificativas claras para a aprovação ou rejeição da "
                            "decisão inicial.",
            async_execution=False,
        )


class Cost_AnalyzeVariationTask():

    def costanalyze_variation(self, agent, order_details):
        return Task(
            description=f"""
                Analise os dados de variação da ordem e fornceça a sua justificativa sobre a aprovação.

                Detalhes da Ordem e Variações Percentuais:
                - 'Material Utilizado': {order_details['Material_Used']}%
                - 'Horas de Setup': {order_details['Setup_Hours']}%
                - 'Horas de Trabalho': {order_details['Labor_Hours']}%
                - 'Horas de Máquina': {order_details['Machine_Hours']}%
                - 'Operação Externa': {order_details['External_Operation']}%
                - 'Padrão x Real': {order_details['Standard_x_Real']}%
                - 'Variação IM x IC': {order_details['Variation_IMxIC']}%
                - 'Variação de Material': {order_details['Variation_Material']}%
                - 'Taxa de Máquina': {order_details['Rate_Machine']}%
                - 'Taxa de Trabalho': {order_details['Rate_Labor']}%
                - 'Taxa de Variação do Trabalho': {order_details['Rate_Var_Labor']}%
                - Ação Prevista pelo Agente: {order_details['Predicted_OUTCOME']}



                Diretrizes:
                - 'Variação IM x IC' maior que 0,02 então Não aprovar, mas se 'Variação IM x IC' for menor que
                0,02 avaliar demais parametros de custo para decidir sobre a aprovação.
                - Ação Prevista como 'REQUER JUSTIFICATIVA FABRICA': Requer justificativa detalhada.
                - Ação Prevista como 'APROVADO COM JUSTIFICATIVA SETOR CUSTOS': Aprovar a ordem com comentários sobre
                os valores.

            """,
            agent=agent,
            expected_output="Forneça uma decisão de aprovação ou rejeição com justificativas claras para cada variação "
                            "analisada.",
            async_execution=False,
        )


class CostReviewVariationTask():
    def cost_review_variation(self, agent, approval_decision, order_details):
        return Task(
            description=f"""
                Utilize a justificativa do agente anterior para elaborar a sua justificativa mais refinada e profissional

                Decisão de Aprovação:
                {approval_decision}
                Variações Percentuais da Ordem:
                -  Valores Negativos igual a melhor rentabilidade
                -  Valores Positivos igual a custo acima do esperado
                {order_details}

                Diretrizes:
                - Verifique se a justificativa é relevante e apropriada para a variação observada.
                - Emita uma decisão de validação com base na revisão da decisão do analista.
                -  'Variação IM x IC' maior que 0,02 então Não aprovar, mas se 'Variação IM x IC' for menor que
                0,02 avaliar demais parametros de custo para decidir sobre a aprovação.

                Formato de resposta esperado:
                - Decisão de Validação: [Validado/Não Validado]
                - Motivo da Decisão: [Explique brevemente a base de sua decisão, focando na relevância e adequação da
                justificativa fornecida].
            """,
            agent=agent,
            expected_output="Forneça uma decisão de validação com as suas justificativas claras para a aprovação ou rejeição",
            async_execution=False,
        )




