import os
import subprocess
from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew
from crewai_tools import ScrapeWebsiteTool

scrape_tool = ScrapeWebsiteTool()

@CrewBase
class POCProjectCrew:
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def researcher(self) -> Agent:
        return Agent(config=self.agents_config['researcher_agent'], verbose=True, tools=[scrape_tool])

    @agent
    def developer(self) -> Agent:
        return Agent(config=self.agents_config['developer_agent'], verbose=True, tools=[scrape_tool])

    @agent
    def qa(self) -> Agent:
        return Agent(config=self.agents_config['qa_agent'], verbose=True , tools=[scrape_tool])

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
            agent=self.researcher(),
            tools=[scrape_tool]
        )

    @task
    def development_task(self) -> Task:
        def execute_development(context):
            research_output = context[0]
            print(f"Research findings: {research_output}")

            if not os.path.exists("poc-project"):
                os.mkdir("poc-project")
            os.chdir("poc-project")

            if not os.path.exists("frontend"):
                subprocess.run(["npx", "create-next-app", "frontend"], check=True)

            if not os.path.exists("backend"):
                subprocess.run(["npx nest", "new", "backend", "--skip-git"], check=True)

            backend_controller_path = "./backend/src/app.controller.ts"
            with open(backend_controller_path, "w") as f:
                f.write("""
import { Controller, Get } from '@nestjs/common';

@Controller('api')
export class AppController {
    @Get()
    fetchData() {
        return { message: 'POC backend is working!' };
    }
}
""")

            print("Development task complete: Projects created with basic functionality.")

        return Task(
            config=self.tasks_config['development_task'],
            action=execute_development,
            agent=self.developer()
        )

    @task
    def qa_task(self) -> Task:
        def execute_qa(context):
            dev_output = context[0]
            print(f"QA checking development output: {dev_output}")

        return Task(
            config=self.tasks_config['qa_task'],
            action=execute_qa,
            agent=self.qa()
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )