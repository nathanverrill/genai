from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_community.chat_models import ChatLiteLLM  # ✅ switch from ChatOpenAI
from dotenv import load_dotenv
load_dotenv()


@CrewBase
class TokensCrew():
    """Tokens crew for comparing model performance"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self, model_name: str, model_id: str, base_url: str, api_key: str):
        self.model_name = model_name

        # ✅ Use ChatLiteLLM with explicit API params
        self.llm = ChatLiteLLM(
            model=model_id,
            api_base=base_url,
            api_key=api_key,
            temperature=0.7
        )

    @agent
    def model_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['model_agent'],
            llm=self.llm,
            verbose=True
        )

    @task
    def generate_response_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_response_task'],
            agent=self.model_agent()
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Tokens crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
