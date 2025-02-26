import os
import json

def extract_scores_from_judgement(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        scores = {}
        for line in lines:
            if '"scores": {' in line:
                # Start reading scores
                for score_line in lines[lines.index(line) + 1:]:
                    if '}' in score_line:
                        break
                    key, value = score_line.strip().strip(',').split(': ')
                    scores[key.strip('"')] = int(value)
                break
    return scores

def main():
    project_reviews_path = 'project_reviews'
    scores_data = []

    for folder_name in os.listdir(project_reviews_path):
        folder_path = os.path.join(project_reviews_path, folder_name)
        if os.path.isdir(folder_path):
            judgement_file_path = os.path.join(folder_path, 'judgement.txt')
            if os.path.exists(judgement_file_path):
                scores = extract_scores_from_judgement(judgement_file_path)
        with open(os.path.join(folder_path, 'scores.json'), 'w') as json_file:
            json.dump( {"scores": scores}, json_file, indent=4)
if __name__ == "__main__":
    main()
