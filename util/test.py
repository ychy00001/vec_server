from dotenv import load_dotenv,dotenv_values
import json
config = dotenv_values()
load_dotenv()

print(config)
print(json.loads(config['OPENAI_API_STOP'])[0])
