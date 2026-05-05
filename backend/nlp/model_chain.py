import json
import os

import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define model chain with fallback options
MODEL_CHAIN = [
    "nvidia/nemotron-3-super-120b-a12b:free",
    "tencent/hy3-preview:free",
    "meta-llama/llama-3.1-70b-instruct:free",
    "openai/gpt-oss-120b:free",
    "poolside/laguna-m.1:free",
    "nvidia/nemotron-3-nano-30b-a3b:free"
]

BEARER_TOKEN = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def call_api_chain(user_message, models=MODEL_CHAIN, timeout=30, reasoning_enabled=True):
    """
    Try the configured models in sequence until one succeeds.
    This function is AI-only and does not generate fallback content.
    """
    
    for model_index, model in enumerate(models, 1):
        print(f"\n{'='*60}")
        print(f"Attempt {model_index}: Trying model - {model}")
        print('='*60)
        
        try:
            response = requests.post(
                url=OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {BEARER_TOKEN}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": user_message}],
                    "reasoning": {"enabled": reasoning_enabled}
                },
                timeout=timeout
            )
            
            # Check if response is successful
            if response.status_code != 200:
                error_msg = response.json().get('error', {})
                print(f" Error Status: {response.status_code}")
                print(f" Error: {error_msg}")
                
                # Check for rate limit or token issues
                if "rate_limit" in str(error_msg).lower() or "token" in str(error_msg).lower():
                    print(f"  Model out of tokens or rate limited. Trying next model...")
                    continue
                else:
                    print(f"  Error occurred. Trying next model...")
                    continue
            
            response_data = response.json()
            
            # Extract content and token info
            content = response_data['choices'][0]['message'].get('content')
            usage = response_data.get('usage', {})
            
            # Get remaining tokens from headers
            remaining_tokens = response.headers.get('x-ratelimit-remaining-tokens', 'N/A')
            
            print(f"\n Success with model: {model}")
            print(f"\nResponse:")
            print(json.dumps(content, indent=2))
            
            print(f"\n{'='*60}")
            print("Token Usage:")
            print('='*60)
            print(f"Prompt Tokens:      {usage.get('prompt_tokens', 0)}")
            print(f"Completion Tokens:  {usage.get('completion_tokens', 0)}")
            print(f"Total Tokens Used:  {usage.get('total_tokens', 0)}")
            print(f"Remaining Tokens:   {remaining_tokens}")
            print('='*60)
            
            return {"status": "success", "model": model, "content": content, "usage": usage}
        
        except requests.exceptions.Timeout:
            print(f" Timeout - Model not responding. Trying next model...")
            continue
        except requests.exceptions.ConnectionError:
            print(f" Connection Error. Trying next model...")
            continue
        except Exception as e:
            print(f" Error: {str(e)}")
            print(f"Trying next model...")
            continue
    
    print(f"\n{'='*60}")
    print(" All models failed!")
    print('='*60)
    return {"status": "failed", "model": None, "content": None, "error": "All configured models failed"}
