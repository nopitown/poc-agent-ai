from poc_agent_ai.crew import POCProjectCrew

def run():
    inputs = {
        "topic": "Is it possible to get the list of medicaments consumed by a patient using the Zus Health API (you can use https://docs.zushealth.com/docs/zus-aggregated-profile as starting point)"
    }
    POCProjectCrew().crew().kickoff(inputs=inputs)
