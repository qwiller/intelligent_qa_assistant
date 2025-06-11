import requests
import json
import os
from typing import Optional, Dict, Any

class LLMIntegrator:
    """Handles interaction with a Large Language Model API."""

    def __init__(self, api_base_url: Optional[str] = None, api_key: Optional[str] = None, model_name: str = "deepseek-r1"):
        """
        Initializes the LLMIntegrator.

        Args:
            api_base_url: The base URL for the LLM API. Can also be set via DEEPSEEK_API_BASE_URL env var.
            api_key: The API key for authentication. Can also be set via DEEPSEEK_API_KEY env var.
            model_name: The specific model to use (e.g., 'deepseek-r1').
        """
        self.api_base_url = api_base_url or os.getenv("DEEPSEEK_API_BASE_URL")
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.model_name = model_name

        if not self.api_base_url:
            raise ValueError("API base URL for DeepSeek is not provided. Set it via constructor or DEEPSEEK_API_BASE_URL environment variable.")
        if not self.api_key:
            # Depending on the API, key might not be needed for all endpoints or if URL itself contains it.
            # For now, let's make it highly recommended.
            print("Warning: API key for DeepSeek is not provided. Set it via constructor or DEEPSEEK_API_KEY environment variable if required by the API.")

        # You might want to customize headers, e.g., for authorization
        self.headers = {
            "Content-Type": "application/json",
            # Add Authorization header if needed, e.g.:
            # "Authorization": f"Bearer {self.api_key}" 
            # Or a custom header like "X-Api-Key": self.api_key
        }
        # If the API key is part of the header, uncomment and adjust the above.
        # For DeepSeek, it's common to use 'Authorization: Bearer YOUR_API_KEY'
        if self.api_key:
             self.headers["Authorization"] = f"Bearer {self.api_key}"

        print(f"LLMIntegrator initialized for model '{self.model_name}' at URL '{self.api_base_url}'")

    def generate_answer(self, query: str, context: str, max_tokens: int = 500, temperature: float = 0.7) -> Optional[str]:
        """
        Generates an answer from the LLM based on the query and context.

        Args:
            query: The user's original query.
            context: The retrieved context from the vector store.
            max_tokens: Maximum number of tokens for the generated answer.
            temperature: Sampling temperature for generation (0.0 to 1.0+).

        Returns:
            The generated answer as a string, or None if an error occurs.
        """
        if not self.api_base_url:
            print("API URL not configured.")
            return None

        # Construct the prompt. This structure is common but might need adjustment
        # based on how DeepSeek-R1 expects prompts for RAG.
        prompt = f"You are an intelligent assistant. Based on the following context, please answer the user's question. If the context does not contain the answer, say so.\n\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer:"
        
        # Define the payload for the API request.
        # The exact structure (e.g., 'prompt' vs 'messages', parameters) 
        # depends heavily on the DeepSeek-R1 API specification.
        # This is a common payload structure for chat-like models:
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "You are an intelligent assistant. Provide answers based on the given context."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            # Add other parameters as supported by DeepSeek-R1 API, e.g., top_p, stream, etc.
        }

        # Example for a completion-style API (if DeepSeek-R1 uses this):
        # payload_completion_style = {
        #     "model": self.model_name,
        #     "prompt": prompt,
        #     "max_tokens": max_tokens,
        #     "temperature": temperature,
        # }
        # current_payload = payload # or payload_completion_style, depending on API
        current_payload = payload

        api_endpoint = f"{self.api_base_url.rstrip('/')}/v1/chat/completions" # Common endpoint for chat models
        # Or for completions: f"{self.api_base_url.rstrip('/')}/v1/completions"

        print(f"Sending request to LLM: {api_endpoint} with model {self.model_name}")
        # print(f"Payload: {json.dumps(current_payload, indent=2)}") # For debugging

        try:
            response = requests.post(api_endpoint, headers=self.headers, json=current_payload, timeout=60) # Added timeout
            response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
            
            response_data = response.json()
            # print(f"LLM Response Data: {json.dumps(response_data, indent=2)}") # For debugging

            # Extract the answer. This depends on the API's response structure.
            # For OpenAI-compatible APIs (like many DeepSeek models aim for):
            if response_data.get("choices") and len(response_data["choices"]) > 0:
                message = response_data["choices"][0].get("message")
                if message and message.get("content"):
                    return message["content"].strip()
                # Fallback for some completion-style responses
                elif response_data["choices"][0].get("text"):
                     return response_data["choices"][0]["text"].strip()
            
            print("Could not extract answer from LLM response.")
            print(f"Full response: {response_data}")
            return "Sorry, I received a response but could not extract an answer."

        except requests.exceptions.RequestException as e:
            print(f"Error calling LLM API: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    print(f"Response content: {e.response.text}")
                except Exception:
                    pass # Ignore if response content is not available or not text
            return "Sorry, I encountered an error while trying to reach the language model."
        except Exception as e:
            print(f"An unexpected error occurred during LLM call: {e}")
            return "Sorry, an unexpected error occurred while processing your request with the language model."

# Example Usage (requires DEEPSEEK_API_BASE_URL and DEEPSEEK_API_KEY environment variables to be set)
if __name__ == '__main__':
    # IMPORTANT: Set your actual API base URL and Key as environment variables or pass them directly.
    # e.g., export DEEPSEEK_API_BASE_URL="https://api.deepseek.com"
    # e.g., export DEEPSEEK_API_KEY="your_actual_api_key"
    
    # Ensure environment variables are set before running this example, or pass directly:
    # llm_client = LLMIntegrator(api_base_url="YOUR_URL", api_key="YOUR_KEY")
    try:
        llm_client = LLMIntegrator()
        
        sample_query = "What is the capital of France?"
        sample_context = "France is a country in Western Europe. Its capital city is Paris, which is known for the Eiffel Tower."
        
        print(f"\nSending query to LLM: '{sample_query}' with context.")
        answer = llm_client.generate_answer(sample_query, sample_context)
        
        if answer:
            print(f"\nLLM Answer:\n{answer}")
        else:
            print("\nFailed to get an answer from LLM.")

        # Example without context (if the model supports direct Q&A)
        # print("\nSending query to LLM: '{sample_query}' without context.")
        # answer_no_context = llm_client.generate_answer(sample_query, "") # Empty context
        # if answer_no_context:
        #     print(f"\nLLM Answer (no context):\n{answer_no_context}")
        # else:
        #     print("\nFailed to get an answer from LLM (no context).")

    except ValueError as ve:
        print(f"Initialization Error: {ve}")
    except Exception as e:
        print(f"An error occurred in the example: {e}")