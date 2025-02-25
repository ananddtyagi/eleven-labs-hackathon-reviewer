import os
from typing import Dict, List
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(
    api_key=os.getenv("ANHTROPIC-KEY"),
    
)
class ProjectDebate:
    def __init__(self, scoring_rubric: Dict[str, str]):
        self.scoring_rubric = scoring_rubric
        
    def load_project_details(self, project_path: str) -> str:
        """Load project description from file."""
        with open(project_path, 'r') as f:
            return f.read()
    
    def initialize_debate(self, project_name: str, description: str):
        """Set up the initial prompt for both debaters."""
        advocate_system_prompt = f"""You are an positive advocate who is responsible for judging projects for the ElevenLabs Hackathon.
        Here is the rubric for judging the projects: {self.scoring_rubric}
        Focus on the positive aspects and potential of the project.
        Provide a structured analysis of its strengths."""
        

        critic_system_prompt = f"""You are an negative critic who is responsible for judging projects for the ElevenLabs Hackathon.
        Here is the rubric for judging the projects: {self.scoring_rubric}
        Focus on potential issues and areas of improvement in the project.
        Provide a structured analysis of its weaknesses."""
        

        
        return advocate_system_prompt, critic_system_prompt
        

    def create_requets(self, project_name: str, description: str):
        """Conduct the debate and get final judgment."""
        advocate_system_prompt, critic_system_prompt = self.initialize_debate(project_name, description)
        project_details = f"""
        Here is the project details, please analyze the project and provide your analysis:
        Project Name: {project_name}
        Project Description: {description}"""

        # First round
        # advocate_response = client.messages.create(
        #     model="claude-3-5-sonnet-20240620",
        #     max_tokens=4000,
        #     system=advocate_system_prompt,
        #     messages=[{"role": "user", "content": project_details}]
        # )
        # critic_response = client.messages.create(
        #     model="claude-3-5-sonnet-20240620",
        #     max_tokens=4000,
        #     system=critic_system_prompt,
        #     messages=[{"role": "user", "content": project_details}]
        # )
        if not os.path.exists(f'project_reviews/{project_name}'):
            os.makedirs(f'project_reviews/{project_name}')
        advocate_request = {
             "custom_id": project_name + "__advocate",
             "params": {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 4000,
                "system": advocate_system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": project_details,
                    }
                ],
            },

        }
        
        critic_request = {
             "custom_id": project_name + "__critic",
             "params": {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 4000,
                "system": critic_system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": project_details,
                    }
                ],  
             }
        }
        
        return advocate_request, critic_request
    def judge_project(self, project_name: str, description: str, advocate_response: str, critic_response: str):
        
        # Final judgment
        judgment_prompt = f"""As an impartial judge, evaluate this project debate:
        Project: {project_name}
        Description: {description}
        
        Advocate's Points:
        {advocate_response}
        
        Critic's Points:
        {critic_response}
        
        Please provide:
        1. A summary of the key points from both sides
        2. A balanced analysis
        3. Scores for each category in this rubric: {self.scoring_rubric}
        4. Final verdict and recommendations
        Provide your response in the following format and make the scores a number between 1 and 10:
        ```json
        {{
            "summary": "<summary>",
            "analysis": "<analysis>",
            "scores": {{"impact": 10, "technical_implementation": 3, "creativity_and_innovation": 5, "pitch_and_presentation": 7}},
            "final_verdict": "<final_verdict>"
        }}
        ```"""
        
        final_judgment = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4000,
            messages=[{"role": "user", "content": judgment_prompt}]
        )
        
        return {
            'project_name': project_name,
            'advocate_response': advocate_response,
            'critic_response': critic_response,
            'final_judgment': final_judgment.content[0].text
        }

    def create_batch_requests(self, projects_dir: str) -> List[Dict]:
        """Create batch requests for all projects in the directory."""
        requests = []
        for filename in os.listdir(projects_dir)[:5]:
            project_name = filename[:-4]
            project_path = os.path.join(projects_dir, filename)
            description = self.load_project_details(project_path)
            advocate_request, critic_request = self.create_requets(project_name, description)   
            requests.append(advocate_request)
            requests.append(critic_request)
            
        return requests
    
    
    # def evaluate_projects(self, projects_dir: str) -> List[Dict]:
    #     """Evaluate all projects in the directory."""
    #     results = []
    #     for filename in os.listdir(projects_dir)[:2]:
    #         if filename.endswith('.txt'):  # Assuming project details are in .txt files
    #             project_name = filename[:-4]  # Remove .txt extension
    #             project_path = os.path.join(projects_dir, filename)
    #             description = self.load_project_details(project_path)
                
    #             result = self.conduct_debate(project_name, description)
    #             results.append(result)
                
    #             # Save results to file
    #             with open(f"debate_results_{project_name}.txt", 'w') as f:
    #                 f.write(f"Project: {project_name}\n\n")
    #                 f.write(f"Advocate's Analysis:\n{result['advocate_response']}\n\n")
    #                 f.write(f"Critic's Analysis:\n{result['critic_response']}\n\n")
    #                 f.write(f"Final Judgment:\n{result['final_judgment']}")
                
    #     return results

    def run_batch_requests(self, requests: List[Dict]):
        response = client.beta.messages.batches.create(requests=requests)
        return response
def main():
    # Example scoring rubric - modify according to your needs
    scoring_rubric = {
        "Impact (25% weight)": "What is the project's potential for long-term success, scalability, and societal impact?",
        "Technical Implementation (25% weight)": "How well has the team implemented the idea? Does the technical implementation have the potential to support the proposed solution?",
        "Creativity and Innovation (25% weight)": "How creative and innovative is the project? Is it a unique and effective solution to a problem?",
        "Pitch and Presentation (25% weight)": "How effectively does the team present and articulate their project, its value proposition, and its potential impact?"
    }
    scoring_rubric = {k: str(v) for k, v in scoring_rubric.items()}
    debater = ProjectDebate(scoring_rubric)
    requests  = debater.create_batch_requests("project_details")
    response = debater.run_batch_requests(requests)
    print(response)
if __name__ == "__main__":
    main()
