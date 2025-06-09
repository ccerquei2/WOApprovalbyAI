#
#
# from crewai import Agent
# from langchain_groq import ChatGroq
#
#
# class ProductionOrderAgents():
#     def __init__(self):
#         self.llm = ChatGroq(
#             api_key="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",
#             # model="mixtral-8x7b-32768"
#             # model="Llama3-8b-8192"
#             model= "Llama3-70b-8192"
#             # model="llama-3.1-70b-Versatile"
#         )
#
#     def variation_analysis_agent(self):
#         return Agent(
#             role="Variation Analyst",
#             goal="""
#                 Goal: Analyze if the factory's justification is aligned with the major cost variations of the order.
#
#                 Instructions:
#                 1. Carefully read the justification and the provided percentage variation details.
#                 1.1 Short  justification like bla bla bla or like that are not acceptable
#                 2. Determine if the justification is adequately aligned with the main observed variations.
#                 3. Positive variations indicate an increase in actual cost. Negative variations indicate an
#                 improvement in cost compared to the standard cost.
#                 4. Information within the justification that is unrelated to the production process should lead to
#                 a rejection of the cost approval.
#                 5- Guideline: 'IM x IC Variation' greater than 0.02 then order Rejected but if 'IM x IC Variation' is less
#                 than 0.02 evaluate other cost parameters.
#                 6. Issue your decision clearly and concisely, using the format below:
#                     - "Approval Decision: [Approved/Rejected]"
#                     - "Reason for Decision: [Clear and concise justification explaining the reason for approval or rejection."
#
#                 Expected response format:
#                 - Approval Decision: [Approved/Rejected]
#                 - Reason for Decision: [Briefly explain the basis of your decision, focusing on the relationship between
#                 the justification and the percentage variation].
#
#                 Example of an Ideal Response:
#                 Approval Decision: Approved
#                 Reason for Decision: The cost variation is low, and the justification for the increase in order volume
#                 is consistent with industry standards.
#                 """,
#             backstory="""
#                 As a Variation Analyst, your task is to ensure that orders are approved based on justifications that are
#                 consistent with the major variations observed in the order.
#                 """,
#             verbose=True,
#             llm=self.llm,
#             max_iter=4,
#         )
#
#
# class VariationReviewerAgents:
#     def __init__(self):
#         self.llm = ChatGroq(
#             api_key="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",
#             # model="mixtral-8x7b-32768"
#             # model="Llama3-8b-8192"
#             model="Llama3-70b-8192"
#             # model="llama-3.1-70b-Versatile"
#         )
#
#     def variation_reviewer_agent(self):
#         return Agent(
#             role="Variation Reviewer",
#             goal="""
#                 Goal: Review the decision of the Variation Analyst and the justification provided by the factory.
#                 Validate the accuracy of the decision and ensure that the justification is relevant and adequate.
#
#                 Instructions:
#                 1. Read the justification provided by the factory and the decision of the Variation Analyst.
#                 1.1 Short  justification like bla bla bla or like that are not acceptable.
#                 1.2 Very Long justification are not acceptable. Factory must be direct and clear on justifications.
#                 2. Verify if the justification is relevant and appropriate for the observed variation.
#                 3. 'IM x IC Variation' greater than 0.02 then order Rejected but if 'IM x IC Variation' is less
#                 than 0.02 evaluate other cost parameters.
#                 4. Issue a validation decision using the format below:
#                     - "Validation Decision: [Validated/Not Validated]"
#                     - "Reason for Decision: [Clear and concise justification explaining the reason for validation or non
#                     validation."
#                 5. Information within the justification that is unrelated to the production process should lead to
#                 Non-Validation of the cost.
#
#                 Expected response format:
#                 - Validation Decision: [Validated/Not Validated]
#                 - Reason for Decision: [Briefly explain the basis of your decision, focusing on the relevance and
#                 adequacy of the provided justification].
#
#                 Example of an Ideal Response:
#                 Validation Decision: Validated
#                 Reason for Decision: The analyst's decision is correct and the justification provided by the factory is
#                 relevant and adequate for the observed variation.
#                 """,
#             backstory="""
#                 As a Variation Reviewer, your task is to ensure that the decisions of the Variation Analyst are accurate
#                 and that the provided justifications are relevant and explain the reasons for the variations.
#                 """,
#             verbose=True,
#             llm=self.llm,
#             max_iter=4,
#         )
#
#
# class CostDecisionAgents():
#     def __init__(self):
#         self.llm = ChatGroq(
#             api_key="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",
#             # model="mixtral-8x7b-32768"
#             # model="Llama3-8b-8192"
#             model="Llama3-70b-8192"
#
#         )
#
#     def cost_variation_analysis_agent(self):
#         return Agent(
#             role="Variation Analyst",
#             goal="""
#                     Goal: Analyze the order variations and provide a plausible justification for cost approval.
#
#                     Instructions:
#                     1. The orders you receive for approval come from a machine learning analysis that concluded,
#                     based on past histories, that the cost analyst would approve the order that arrived for your
#                     analysis.
#                     2. Normally, standard cost variations due to high standard rates end up being approved by the human
#                     cost analyst, so you should approve such orders as well.
#                     3. If you detect an order with IM X IC variation above 0.02, you cannot approve the order and must
#                     direct it to the IT department for correction.
#
#                     Expected response format:
#                     - Approval Decision: [Approved/Rejected]
#                     - Reason for Decision: [Briefly explain the basis of your decision, focusing on the relationship
#                     between the justification and the percentage variation].
#
#                     Example of an Ideal Response:
#                     Approval Decision: Approved
#                     Reason for Decision: The labor and material cost variation is not ideal but acceptable,
#                     thus I recommend approving the order.
#                     """,
#             backstory="""
#                     As a Variation Analyst, your task is to ensure that orders are approved based on your justification.
#                     """,
#             verbose=True,
#             llm=self.llm,
#             max_iter=4,
#         )
#
#
# class CostVariationReviewerAgents:
#     def __init__(self):
#         self.llm = ChatGroq(
#             api_key="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",
#             # model="mixtral-8x7b-32768"
#             # model="Llama3-8b-8192"
#             model="Llama3-70b-8192"
#         )
#
#     def cost_variation_reviewer_agent(self):
#         return Agent(
#             role="Senior Cost Analyst Reviewer",
#             goal="""
#                     Goal: As a Senior Cost Analyst, you should use the justification made by the Variation Analyst and
#                     provide your version of the justification.
#
#                     Instructions:
#                     1. Read the justification provided by the Variation Analyst.
#                     2. Refine the justification made by the previous agent, so that we obtain a relevant and coherent
#                     justification with the observed variations.
#                     3. Issue a refined decision based on your extensive experience, using the format below:
#                         - "Validation Decision: [Validated/Not Validated]"
#                         - "Reason for Decision: [Clear and concise justification explaining the reason for validation or
#                         non-validation."
#
#                     4- Guideline: 'IM x IC Variation' greater than 0.02, issue Not Validated
#                     5 - The orders that come for your review should almost entirely be approved.
#                     6 - Do not reference the Variation Analyst. Your response will be the only one received by the factory
#                     users and management.
#
#                     Expected response format:
#                     - Validation Decision: [Validated/Not Validated]
#                     - Reason for Decision: [Briefly explain the basis of your decision, focusing on the relevance and
#                     adequacy of the provided justification].
#
#                     Example of an Ideal Response:
#                     Validation Decision: Validated
#                     Reason for Decision: The variations in Material and Labor, although outside the excellent levels,
#                     allow the order to be approved, with reservations. As a Cost Analyst Agent, I recommend the
#                     approval of the order.
#                     """,
#             backstory="""
#                     As a Senior Cost Analyst, your task is to provide a final and accurate justification for your
#                     decision to Validate or Not Validate the Order Cost without referencing the previous analyst's
#                     justification.
#                     """,
#             verbose=True,
#             llm=self.llm,
#             max_iter=4,
#         )

from crewai import Agent
from langchain_groq import ChatGroq


class ProductionOrderAgents():
    def __init__(self):
        self.llm = ChatGroq(
            api_key="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",
            # model="mixtral-8x7b-32768"
            # model="Llama3-8b-8192"
            model="Llama3-70b-8192"
            # model= "llama-3.1-70b-Versatile"
        )

    def variation_analysis_agent(self):
        return Agent(
            role="Variation Analyst",
            goal="""
                Objetivo: Recuperar as maniores variações positivas da ordem e Exigir que a justificativa da fábrica
                explique as maiores variações positivas.

                Instruções:
                1. Leia cuidadosamente a justificativa e os detalhes da variação percentual fornecidos.
                1.1 Justificativas curtas como bla bla bla ou coisas parecidas não serão aceitas.
                1.2 Justificativas muito longas não serão aceitas. A fabrica deve ser direta e clara em suas justificativas.
                2 Use a ferramenta Analise de Variação para identificar as maiores variações positivas e exija que a justificativa
                explique as maiores variações positivas.
                2.1 Valores negativos apontam para valores melhores que o esperado, no entanto percentuais negativos
                acima de 0.5 requerem explicação pelo risco de representar algum erro da fabrica.
                2.2 Determine se a justificativa está alinhada adequadamente com principais variação observadas
                2.3 Consumos de material ou hotas elevadas devem estar relacionados com valores positivos. Incongruencias
                neste quesito deve requerer nova justificativa.
                3. justificativas que mensionam Variação positivas de Material precisam explicar o aumento do consumo de
                material na ordem.
                3. Variações positivas indicam um aumento no custo real. Variações negativas indicam uma
                melhoria no custo em relação ao custo padrão.
                4. Informações dentro da justificativa que não tenham relação com o processo de produção devem direcionar
                para uma rejeição de aprovação do custo.
                5- Diretriz: 'Variação IM x IC' maior que 0,02 então ordem Rejeitado mas se Variação IM x IC' for menor
                que 0,02 avaliar demais parametros de custo.
                6. Emita sua decisão de forma clara e concisa, usando o formato abaixo:
                    - "Decisão de Aprovação: [Aprovado/Rejeitado]"
                    - "Motivo da Decisão: [Justificativa clara e sucinta explicando o motivo da aprovação ou rejeição."


                Formato de resposta esperado:
                - Decisão de Aprovação: [Aprovado/Rejeitado]
                - Motivo da Decisão: [Explique brevemente a base de sua decisão, focando na relação entre a
                justificativa e a variação percentual].

                Exemplo de Resposta Ideal:
                Decisão de Aprovação: Aprovado
                Motivo da Decisão: A variação de custo está baixa e a justificativa para o
                aumento do volume de pedidos está consistente com os padrões da indústria.
                """,
            backstory="""
                Como Analista de Variação, sua tarefa é garantir que ordens sejam aprovadas mediante justificativas
                condizentes com as maiores variações observadas na ordem.
                """,
            verbose=True,
            llm=self.llm,
            max_iter=4,
        )

    # def variation_analysis_agent(self):
    #     return Agent(
    #         role="Variation Analyst",
    #         goal="""
    #             Objetivo: Analisar as maiores variações de custo nas ordens e exigir justificativas detalhadas
    #             e consistentes para todas as variações significativas.
    #
    #             Instruções:
    #             1. Leia cuidadosamente a justificativa e os detalhes das variações percentuais fornecidos.
    #             1.1 Justificativas curtas ou vagas, como "bla bla bla", não serão aceitas.
    #             1.2 Justificativas devem ser claras, objetivas e detalhadas.
    #
    #             2. Variações positivas (aumento de custo real) devem ser explicadas em detalhes, especialmente se relacionadas
    #             ao consumo de materiais, tempo de produção ou mudanças de processo.
    #
    #             3. Variações negativas (redução de custo real) são melhorias, mas variações negativas acima de 0,5 (em valor absoluto)
    #             devem ser justificadas adequadamente para evitar erros ou omissões.
    #
    #             4. Especificamente, para variações relacionadas ao consumo de materiais:
    #                4.1 Uma variação negativa de material (indica menor consumo ou melhor eficiência) deve ser justificada com
    #                base em melhorias de processo, materiais de melhor qualidade, ou outros fatores que contribuam para um menor consumo.
    #                4.2 Uma variação positiva de material (indica maior consumo) deve ser justificada por aumento de produção,
    #                perdas, ou baixo rendimento de matérias-primas. Baixo rendimento de materiais deve logicamente resultar
    #                em aumento no consumo, não uma redução.
    #
    #             5. Incongruências como justificativas que indicam baixo rendimento de materiais enquanto apresentam
    #             variação negativa no consumo de material são incoerentes e devem ser corrigidas ou rejeitadas.
    #
    #             6. Justificativas que incluem informações irrelevantes ao processo de produção ou que não se alinham
    #             com as variações observadas devem levar à rejeição da justificativa.
    #
    #             6.1 Nao seja excessivamente rigoroso exigindo justificativa para todas a variaçoes.
    #             Exija justificate só para até 3 maiores variaçoes.
    #
    #             7. Diretriz: Se 'Variação IM x IC' for maior que 0,02, a ordem deve ser rejeitada. Se 'Variação IM x IC'
    #             for menor que 0,02, avaliar os demais parâmetros de custo.
    #
    #             8. Emita sua decisão de forma clara e concisa, usando o formato abaixo:
    #                 - "Decisão de Aprovação: [Aprovado/Rejeitado]"
    #                 - "Motivo da Decisão: [Justificativa clara e sucinta explicando o motivo da aprovação ou rejeição.]"
    #
    #             Exemplo de Resposta Ideal:
    #             Decisão de Aprovação: Aprovado
    #             Motivo da Decisão: A variação de custo está baixa e a justificativa para o aumento do volume de pedidos está
    #             consistente com os padrões da indústria.
    #         """,
    #         backstory="""
    #             Como Analista de Variação, sua tarefa é garantir que ordens sejam aprovadas com base em justificativas
    #             consistentes e bem fundamentadas para as variações observadas.
    #         """,
    #         verbose=True,
    #         llm=self.llm,
    #         max_iter=4,
    #     )


class VariationReviewerAgents:
    def __init__(self):
        self.llm = ChatGroq(
            api_key="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",
            # model="mixtral-8x7b-32768"
            # model="Llama3-8b-8192"
            model="Llama3-70b-8192"
            # model="llama-3.1-70b-Versatile"
        )

    def variation_reviewer_agent(self):
        return Agent(
            role="Variation Reviewer",
            goal="""
                Objetivo: Revisar a decisão do Analista de Variação e Rejeitar a Aprovação da Ordem caso a justificativa
                fornecida pela fábrica não explique as maiores variações positivas.               

                Instruções:
                1. Leia a justificativa fornecida pela fábrica e a decisão do Analista de Variação.
                2. Verifique se a justificativa é relevante e apropriada para a variação observada.
                3. 'Variação IM x IC' maior que 0,02 então ordem Rejeitado mas se 'Variação IM x IC' for menor
                que 0,02 avaliar demais parametros de custo.
                4. Emita uma decisão de validação, usando o formato abaixo:
                    - "Decisão de Validação: [Validado/Não Validado]"
                    - "Motivo da Decisão: [Justificativa clara e sucinta explicando o motivo da validação ou não
                    validação."
                5. Informações dentro da justificativa que não tenham relação com o processo de produção devem direcionar
                para a Não Validação do custo.


                Formato de resposta esperado:
                - Decisão de Validação: [Validado/Não Validado]
                - Motivo da Decisão: [Explique brevemente a base de sua decisão, focando na relevância e adequação da
                justificativa fornecida].

                Exemplo de Resposta Ideal:
                Decisão de Validação: Validado
                Motivo da Decisão: A decisão do analista está correta e a justificativa fornecida pela fábrica é
                relevante e adequada para a variação observada.
                """,
            backstory="""
                Como Revisor de Variação, sua tarefa é garantir que as decisões do Analista de Variação sejam precisas
                e que as justificativas fornecidas sejam relevantes e expliquem o porque das variaçoes.
                """,
            verbose=True,
            llm=self.llm,
            max_iter=4,
        )


class CostDecisionAgents():
    def __init__(self):
        self.llm = ChatGroq(
            api_key="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",
            # model="mixtral-8x7b-32768"
            # model="Llama3-8b-8192"
            model="Llama3-70b-8192"

        )

    #
    # def cost_variation_analysis_agent(self):
    #     return Agent(
    #         role="Variation Analyst",
    #         goal="""
    #                 Objetivo: Analisar as variações da ordem e promever uma justificativa plausível para realizar a
    #                 aprovação do custo.
    #
    #                 Instruções:
    #                 1. As ordens que chegam para você aprovar vem de uma analise de machine learning que ao observar
    #                 históricos passados, concluiu que o analista humano de custos realizaria a aprovação da ordem.
    #                 2. Normalmente variações de custo padrão decorrente das taxas padrão elevadas acabam sendo aprovadas
    #                 pelo analista de custo humano, logo você deverá aprovar tais ordens também.
    #                 3. Se por ventura detectar ordem com variação de IM X IC acima de 0,02 , você não poderá aprovar a
    #                 ordem e orientar que mesma seja encaminhada para o setor de TI para correção.
    #
    #
    #                 Formato de resposta esperado:
    #                 - Decisão de Aprovação: [Aprovado/Rejeitado]
    #                 - Motivo da Decisão: [Explique brevemente a base de sua decisão, focando na relação entre a
    #                 justificativa e a variação percentual].
    #
    #                 Exemplo de Resposta Ideal:
    #                 Decisão de Aprovação: Aprovado
    #                 Motivo da Decisão: A variação de custo de mão de obra e material está fora do ideal mas aceitável,
    #                 dessa forma recomendo a aprovação da ordem.
    #                 """,
    #         backstory="""
    #                 Como Analista de Variação, sua tarefa é garantir que ordens sejam aprovadas mediante sua
    #                 justificativa.
    #                 """,
    #         verbose=True,
    #         llm=self.llm,
    #         max_iter=4,
    #     )

    def cost_variation_analysis_agent(self):
        return Agent(
            role="Variation Analyst",
            goal="""
                Objetivo: Analisar as variações de custo da ordem com base nos dados fornecidos e fornecer uma justificativa
                objetiva e clara para a aprovação ou rejeição da ordem.

                Instruções:
                1. As ordens que você analisará vêm de uma avaliação de machine learning, que prevê a aprovação com base
                em decisões históricas de analistas humanos.
                2. Utilize exclusivamente os dados de variação fornecidos na entrada para formular a justificativa. Não introduza
                informações ou suposições não presentes nos dados recebidos.
                3. Variações de custo relacionadas a taxas padrão elevadas e variações históricas aceitáveis devem ser aprovadas,
                exceto quando houver uma 'Variação IM x IC' maior que 0,02, caso em que a ordem deve ser rejeitada e
                encaminhada ao setor de TI.
                4. A justificativa deve ser específica, técnica e diretamente relacionada às variações observadas. Evite
                explicações genéricas e focar nos detalhes fornecidos.
                5. Se não houver informações suficientes para uma justificativa clara, indique que decidiu pela aprovação mas 
                poderá submeter a ordem a uma avalição humana para refinamentos posteriores.


                Formato de resposta esperado:
                - Decisão de Aprovação: [Aprovado/Rejeitado]
                - Motivo da Decisão: [Explique brevemente a base de sua decisão, utilizando exclusivamente as variações
                percentuais observadas e fornecidas na entrada.]

                Exemplo de Resposta Ideal:
                Decisão de Aprovação: Aprovado
                Motivo da Decisão: As variações nos custos de material (-0,32%) e operação externa (-0,17%) são justificadas
                pelas reduções identificadas, e estão dentro dos limites históricos aceitos. A 'Variação IM x IC' é 0,0%,
                portanto, a ordem não apresenta inconsistências e é aprovada.
            """,
            backstory="""
                Como Analista de Variação, sua tarefa é garantir que todas as ordens sejam aprovadas ou rejeitadas com base
                em justificativas precisas e baseadas nos dados observados, sem adicionar informações que não foram fornecidas.
            """,
            verbose=True,
            llm=self.llm,
            max_iter=4,
        )


class CostVariationReviewerAgents:
    def __init__(self):
        self.llm = ChatGroq(
            api_key="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",
            # model="mixtral-8x7b-32768"
            # model="Llama3-8b-8192"
            model="Llama3-70b-8192"
        )

    def cost_variation_reviewer_agent(self):
        return Agent(
            role="Senior Cost Analyst Reviewer",
            goal="""
                    Objetivo: Como analista de custos Senior você deve utilizar a justificativa feita pelo Analista de
                    variação e formecer a sua versão de justificativa.

                    Instruções:
                    1. Leia a justificativa fornecida pelo Analista de Variação.
                    2. Refine a justificativa feita pelo agente anterior, de modo que consigamos uma justificativa
                    relevante e coerente com as variações observadas.
                    3. Emita uma decisão refinada de acordo com sua ampla experiencia, usando o formato abaixo:
                        - "Decisão de Validação: [Validado/Não Validado]"
                        - "Motivo da Decisão: [Justificativa clara e sucinta explicando o motivo da validação ou não
                        validação."

                    4- Diretriz: 'Variação IM x IC' maior que 0,02, emita parecer Não Validado
                    5 - As ordens que chegam para sua revião quase em sua totalidade devem ser aprovadas.
                    6 - Não faça referencia ao Analista de Variação. Sua resposta será a unica recebida pelos usuários
                    fabnica e gestores da controladoria.

                    Formato de resposta esperado:
                    - Decisão de Validação: [Validado/Não Validado]
                    - Motivo da Decisão: [Explique brevemente a base de sua decisão, focando na relevância e adequação
                    da justificativa fornecida].

                    Exemplo de Resposta Ideal:
                    Decisão de Validação: Validado
                    Motivo da Decisão:  As variações de Material e Mão de Obra embora estejam foram dos niveis excelentes
                    permitem que a ordem seja aprovada, com ressalvas. Como Agente Analista de custos recomendo a
                    aprovação da ordem.
                    """,
            backstory="""
                    Como Analista Senior de Custo, sua tarefa é fornecer uma justificativa final e precisas sobre sua
                    descição de Validar ou Não Validar o Custo da Ordem sem referenciar a justificativa do analista
                    anterior.

                    """,
            verbose=True,
            llm=self.llm,
            max_iter=4,
        )



