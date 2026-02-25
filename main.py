import os, argparse

from google import genai
from google.genai import types
from dotenv import load_dotenv

from prompts import system_prompt
from call_function import *

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
response = client.models.generate_content(
    model='gemini-2.5-flash', 
    contents=messages, 
    config=types.GenerateContentConfig(
        tools=[available_functions], 
        system_instruction=system_prompt, 
        temperature=0,
        ),
    )

if response.usage_metadata is None:
    raise RuntimeError("Failed API request")

if args.verbose:
    print(f"User prompt: {args.user_prompt}")
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
    
if response.function_calls:
    function_results = []

    for function_call in response.function_calls:
        function_call_result = call_function(function_call, verbose=args.verbose)

        if not function_call_result.parts:
            raise RuntimeError(f"Function call returned no parts: {function_call.name}")
        
        part = function_call_result.parts[0]

        if part.function_response is None:
            raise RuntimeError(f"FunctionResponse is None for: {function_call.name}")
        if part.function_response.response is None:
            raise RuntimeError(f"Function response is empty for: {function_call.name}")

        function_results.append(part)

        if args.verbose:
            print(f"-> {part.function_response.response}")      
else:
    print(response.text)