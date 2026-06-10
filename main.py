"""
Viral Post Refiner: A CLI tool to refine an original viral post based on its comment section.

Usage Examples:
    python viral_post_refiner.py --post "Original post text" --comments "Raw comment text"
    python viral_post_refiner.py --post "Original post text" --comments "Raw comment text" --api-key "YOUR_API_KEY" --api-url "https://api.openai.com/v1/completions"

Args:
    --post (str): The original viral post text.
    --comments (str): The raw text of the comment section.
    --api-key (str, optional): The API key for the LLM API. Defaults to None.
    --api-url (str, optional): The URL of the LLM API. Defaults to "https://api.openai.com/v1/completions".
    --output-dir (str, optional): The directory to output the refined post and changelog. Defaults to the current working directory.

Returns:
    A refined version of the original post, addressing valid critiques and correcting facts in the comments while maintaining the original tone.
"""

import argparse
import os
import requests
from typing import Optional

def parse_args() -> argparse.Namespace:
    """
    Parse the command-line arguments.

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Viral Post Refiner")
    parser.add_argument("--post", type=str, required=True, help="The original viral post text")
    parser.add_argument("--comments", type=str, required=True, help="The raw text of the comment section")
    parser.add_argument("--api-key", type=str, help="The API key for the LLM API")
    parser.add_argument("--api-url", type=str, default="https://api.openai.com/v1/completions", help="The URL of the LLM API")
    parser.add_argument("--output-dir", type=str, default=os.getcwd(), help="The directory to output the refined post and changelog")
    return parser.parse_args()

def get_api_key() -> Optional[str]:
    """
    Get the API key from the environment variable or the command-line argument.

    Returns:
        Optional[str]: The API key, or None if not found.
    """
    api_key = os.environ.get("API_KEY")
    if api_key is None:
        args = parse_args()
        api_key = args.api_key
    return api_key

def send_prompt_to_llm_api(prompt: str, api_key: str, api_url: str) -> str:
    """
    Send a prompt to the LLM API and return the response.

    Args:
        prompt (str): The prompt to send to the LLM API.
        api_key (str): The API key for the LLM API.
        api_url (str): The URL of the LLM API.

    Returns:
        str: The response from the LLM API.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "text-davinci-003",
        "prompt": prompt,
        "max_tokens": 2048,
        "temperature": 0.7
    }
    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"Failed to send prompt to LLM API: {response.text}")
    return response.json()["choices"][0]["text"]

def refine_post(original_post: str, comments: str, api_key: str, api_url: str) -> str:
    """
    Refine the original post based on the comment section.

    Args:
        original_post (str): The original viral post text.
        comments (str): The raw text of the comment section.
        api_key (str): The API key for the LLM API.
        api_url (str): The URL of the LLM API.

    Returns:
        str: The refined post.
    """
    prompt = f"Rewrite the post to address valid critiques and correct facts in the comments while maintaining the original tone. Original post: {original_post}. Comments: {comments}"
    response = send_prompt_to_llm_api(prompt, api_key, api_url)
    return response

def generate_changelog(original_post: str, refined_post: str) -> str:
    """
    Generate a changelog based on the original post and the refined post.

    Args:
        original_post (str): The original viral post text.
        refined_post (str): The refined post.

    Returns:
        str: The changelog.
    """
    changes = []
    for i in range(max(len(original_post), len(refined_post))):
        if i >= len(original_post):
            changes.append(f"Added: {refined_post[i]}")
        elif i >= len(refined_post):
            changes.append(f"Removed: {original_post[i]}")
        elif original_post[i] != refined_post[i]:
            changes.append(f"Changed: {original_post[i]} -> {refined_post[i]}")
    changelog = "\n".join(changes)
    return changelog

def main() -> None:
    """
    The main function.
    """
    args = parse_args()
    api_key = get_api_key()
    if api_key is None:
        print("No API key found. Please set the API_KEY environment variable or provide the --api-key argument.")
        return
    refined_post = refine_post(args.post, args.comments, api_key, args.api_url)
    changelog = generate_changelog(args.post, refined_post)
    with open(os.path.join(args.output_dir, "post_v2.txt"), "w") as f:
        f.write(refined_post)
    with open(os.path.join(args.output_dir, "changelog.md"), "w") as f:
        f.write(changelog)
    print("Refined post and changelog generated successfully.")

if __name__ == "__main__":
    main()