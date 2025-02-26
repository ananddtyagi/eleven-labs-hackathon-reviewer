import os
import json

# Define directories
project_details_dir = 'project_details'
project_reviews_dir = 'project_reviews'
output_dir = 'complete_project_review_data'

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Iterate over each file in the project_details directory
for filename in os.listdir(project_details_dir):
    if filename.endswith('.txt'):
        # Extract project details
        with open(os.path.join(project_details_dir, filename), 'r') as file:
            project_details = file.read()

        # Truncate the filename
        truncated_name = filename[:-4][:50]

        # Find the corresponding folder in project_reviews
        review_folder = os.path.join(project_reviews_dir, truncated_name)
        if os.path.isdir(review_folder):
            # Initialize a dictionary to hold all data
            project_data = {
                'project_details': project_details,
                'advocate': '',
                'critic': '',
                'judgement': '',
                'scores': {}
            }

            # Read data from advocate.txt, critic.txt, judgement.txt, and scores.json
            for review_file in ['advocate.txt', 'critic.txt', 'judgement.txt', 'scores.json']:
                review_path = os.path.join(review_folder, review_file)
                if os.path.exists(review_path):
                    with open(review_path, 'r') as rf:
                        if review_file == 'scores.json':
                            project_data['scores'] = json.load(rf)['scores']
                        else:
                            project_data[review_file[:-4]] = rf.read()

            # Save the compiled data to a JSON file
            output_file_path = os.path.join(output_dir, f"{truncated_name}.json")
            with open(output_file_path, 'w') as output_file:
                json.dump(project_data, output_file, indent=4)
