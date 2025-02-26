
import anthropic
from dotenv import load_dotenv
import os
load_dotenv()
client = anthropic.Anthropic(
    api_key=os.getenv("ANHTROPIC-KEY"),
    
)

# Stream results file in memory-efficient chunks, processing one at a time
for result in client.messages.batches.results(
    "msgbatch_id",
):
    match result.result.type:
        case "succeeded":
            print(f"Success! {result.custom_id}")
            print(result.custom_id.split("__")[0])
            folder_name, file_name = result.custom_id.split("__")
            with open(f'project_reviews/{folder_name}/{file_name}.txt', 'w') as f:
                f.write(result.result.message.content[0].text)
        case "errored":
            if result.result.error.type == "invalid_request":
                # Request body must be fixed before re-sending request
                print(f"Validation error {result.custom_id}")
            else:
                # Request can be retried directly
                print(f"Server error {result.custom_id}")
        case "expired":
            print(f"Request expired {result.custom_id}")