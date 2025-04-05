from openai import OpenAI


# Configure the client with the provided API key and base URL
def client_config() -> OpenAI:
    client = OpenAI(
        api_key = "YOUR_API_KEY",
        base_url = "YOUR_BASE_URL",
    )
    return client