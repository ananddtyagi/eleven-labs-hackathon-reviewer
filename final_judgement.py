import os
from typing import Any, Dict, List
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
    
    def judge_project_request(self, project_name: str, description: str, advocate_response: str, critic_response: str):
        
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
        
        return {
            "custom_id": project_name[:50] + "__judgement",
            "params": {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 4000,
                "messages": [{"role": "user", "content": judgment_prompt}]
            }
        }
        # final_judgment = client.messages.create(
        #     model="claude-3-5-sonnet-20240620",
        #     max_tokens=4000,
        #     messages=[{"role": "user", "content": judgment_prompt}]
        # )
        
        # return {
        #     'project_name': project_name,
        #     'advocate_response': advocate_response,
        #     'critic_response': critic_response,
        #     'final_judgment': final_judgment.content[0].text
        # }
    
    
    def evaluate_projects(self, projects_dir: str) -> List[Dict]:
        """Evaluate all projects in the directory."""
        requests = []
        for filename in os.listdir(projects_dir):
            if filename.endswith('.txt'):  # Assuming project details are in .txt files
                project_name = filename[:-4]  # Remove .txt extension
                project_path = os.path.join(projects_dir, filename)
                description = self.load_project_details(project_path)
                advocate_response = self.load_project_details(os.path.join("project_reviews", f"{project_name[:50]}", f"advocate.txt"))
                critic_response = self.load_project_details(os.path.join("project_reviews", f"{project_name[:50]}", f"critic.txt"))
                request = self.judge_project_request(project_name, description, advocate_response, critic_response)
                requests.append(request)
                
                # # Save results to file
                # with open(f"debate_results_{project_name}.txt", 'w') as f:
                #     f.write(f"Project: {project_name}\n\n")
                #     f.write(f"Advocate's Analysis:\n{result['advocate_response']}\n\n")
                #     f.write(f"Critic's Analysis:\n{result['critic_response']}\n\n")
                #     f.write(f"Final Judgment:\n{result['final_judgment']}")
                
        return requests

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
    requests: List[Dict[Any, Any]]    = debater.evaluate_projects("project_details")
    response = debater.run_batch_requests(requests)
    print(response)
if __name__ == "__main__":
    main()
