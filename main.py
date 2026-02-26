import os
import argparse

from google import genai
from google.genai import types
from dotenv import load_dotenv

from prompts import system_prompt
from call_function import call_function, available_functions


#Load the Gemni API key from environment
def load_api_key():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not found in environment.")
    return api_key

#Parse CLI arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Simple Gemini CLI chatbot')
    parser.add_argument("user_prompt", type=str, help="user_prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    return parser.parse_args()

#Wrap the user prompt in the message structure required by Gemini
def build_messages(user_prompt):
    return [types.Content(role="user", parts=[types.Part(text=user_prompt)])]

#Send the messages to Gemnini and return the response
def generate_response(api_key, messages):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt,
            temperature=0,
        ),
    )
    if response.usage_metadata is None:
        raise RuntimeError("Failed API request: no usage metadata.")
    return response

#Process any function calls returned by the model
def handle_function_calls(response, verbose=False):
    if not response.function_calls:
        return None
    
    function_results = []

    for function_call in response.function_calls:
        result = call_function(function_call, verbose=verbose)

        if not result.parts:
            raise RuntimeError(f"Function call returned no parts: {function_call.name}")
        
        part = result.parts[0]

        if part.function_response is None:
            raise RuntimeError(f"FunctionResponse is None for: {function_call.name}")
        if part.function_response.response is None:
            raise RuntimeError(f"Function response is empty for: {function_call.name}")

        function_results.append(part)

        if verbose:
            print(f"-> {part.function_response.response}")

    return function_results

def main():
    args = parse_args()
    api_key = load_api_key()
    messages = build_messages(args.user_prompt)
    response = generate_response(api_key, messages)

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    function_results = handle_function_calls(response, verbose=args.verbose)

    if not function_results:
        print(response.text)
    
if __name__ == "__main__":
    main()

