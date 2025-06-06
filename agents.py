from crewai import Agent
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from decrypt import decrypt_keys

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="__init__")



class BaseAgent:
    def __init__(self, model_choice=None):
        # Define o modelo a ser usado, ou o padrão se nenhum for especificado
        self.model_choice = model_choice if model_choice else "Llama3-70b-8192"
        self.groq_llm, self.openai_llm = self.choice_llms()

    def choice_llms(self):
        groq_llm = ChatGroq(

            api_key=decrypt_keys("groq_api_key"),
            model=self.model_choice  # Usa o modelo especificado ou o padrão
        )

        openai_llm = ChatOpenAI(

            api_key=decrypt_keys("openai_api_key"),
            model="gpt-4o-mini"
        )
        return groq_llm, openai_llm

    def get_llm(self):
        # Retorna o modelo escolhido
        return self.groq_llm


class ProductionOrderAgents():
     def variation_analysis_agent(self, model_llm):
        return Agent(
            role="Variation Analyst",
            goal="""
                Objetivo: Recuperar as maniores variações positivas da ordem e Exigir que a justificativa da fábrica
                explique as maiores variações positivas.

                Instruções:
                1. Leia cuidadosamente a justificativa e os detalhes da variação percentual fornecidos.
                1.1 Justificativas curtas que contenham bla bla bla ou coisas parecidas não serão aceitas.
                1.2 Justificativas que contenham assuntos não relacionados ao processo fabríl não serão aceitas.
                1.3 Justificativas muito longas não serão aceitas. A fabrica deve ser direta e clara em suas justificativas.               
                2 Use a ferramenta Analise de Variação para identificar as variações positivas e exija que a justificativa
                explique as variações positivas.
                2.1 Valores negativos apontam para valores melhores que o esperado, no entanto percentuais negativos
                acima de 0.5 requerem explicação pelo risco de representar algum erro da fabrica.
                2.2 Determine se a justificativa está alinhada adequadamente com principais variação observadas
                2.3 Consumos de material ou horas elevadas devem estar relacionados com valores positivos. Incongruencias
                neste quesito deve requerer nova justificativa.
                3. justificativas que mensionam Variação positivas de Material precisam explicar o aumento do consumo de
                material na ordem.
                3. Variações positivas indicam um aumento no custo real. Variações negativas indicam uma
                melhoria no custo em relação ao custo padrão.
                4. Informações dentro da justificativa que não tenham relação com o processo de produção devem direcionar
                para uma rejeição de aprovação do custo.
                5. Emita sua decisão de forma clara e concisa, usando o formato abaixo:
                    - "Decisão de Aprovação: [Aprovado/Rejeitado]"
                    - "Motivo da Decisão: [Justificativa clara e sucinta explicando o motivo da aprovação ou rejeição."


                Formato de resposta esperado:
                - Decisão de Aprovação: [Aprovado/Rejeitado]
                - Motivo da Decisão: [Explique brevemente a base de sua decisão, focando na relação entre a
                justificativa e a variação].

                Exemplo de Resposta Ideal:
                Decisão de Aprovação: Aprovado
                Motivo da Decisão: As variaçções de quantidade de material e quantidade de horas foram justificadas 
                pela fábrica de forma consistente. As variações estão condizentes com os limites praticados na empresa.
                """,
            backstory="""
                Como Analista de Variação, sua tarefa é garantir que ordens sejam aprovadas mediante justificativas
                condizentes às variações observadas na ordem.
                """,
            verbose=True,
            llm=model_llm,
            max_iter=4,
        )



class VariationReviewerAgents():

    def variation_reviewer_agent(self, model_llm):
        return Agent(
            role="Variation Reviewer",
            goal="""
                Objetivo: Revisar a decisão do Analista de Variação e Rejeitar a Aprovação da Ordem caso a justificativa
                fornecida pela fábrica não explique as variações positivas.               
                
                Instruções:
                1. Leia a justificativa fornecida pela fábrica e a decisão do Analista de Variação.
                2. Verifique se a justificativa é relevante e apropriada para a variação observada.
                3. Emita uma decisão de validação, usando o formato abaixo:
                    - "Decisão de Validação: [Validado/Não Validado]"
                    - "Motivo da Decisão: [Justificativa clara e sucinta explicando o motivo da validação ou não 
                    validação."
                4. Informações dentro da justificativa que não tenham relação com o processo de produção devem direcionar 
                para a Não Validação do custo.
                5. A falta de justificativa para uma determinada variação positiva deve direcionar para rejeição da 
                aprovação.


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
            llm=model_llm,
            max_iter=4,
        )




class CostDecisionAgents():
    # def __init__(self):
    #     self.llm = ChatGroq(
    #             api_key="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",
    #             # model="mixtral-8x7b-32768"
    #             # model="Llama3-8b-8192"
    #             model="Llama3-70b-8192"
    #
    #     )
    #

    def cost_variation_analysis_agent(self, model_llm):
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
            llm=model_llm,
            max_iter=4,
        )


class CostVariationReviewerAgents:
    # def __init__(self):
    #     self.llm = ChatGroq(
    #         api_key="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",
    #         # model="mixtral-8x7b-32768"
    #         # model="Llama3-8b-8192"
    #         model="Llama3-70b-8192"
    #     )

    def cost_variation_reviewer_agent(self, model_llm):
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
            llm=model_llm,
            max_iter=4,
        )



