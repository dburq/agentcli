import os, argparse
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
if api_key is None:
    raise RuntimeError("Failed API request")

parser = argparse.ArgumentParser(description='Simple Gemini CLI chatbot')
parser.add_argument("user_prompt", type=str, help="user_prompt")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()

messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

client = genai.Client(api_key=api_key)
response = client.models.generate_content(model='gemini-2.5-flash', contents=messages)
if response.usage_metadata is None:
    raise RuntimeError("Failed API request")

if args.verbose:
    print(f"User prompt: {args.user_prompt}")
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
    
print(response.text)
