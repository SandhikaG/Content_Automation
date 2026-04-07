import requests
from bs4 import BeautifulSoup


def extract_webpage_content(url: str):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove scripts/styles
        for tag in soup(["script", "style", "noscript"]):
            tag.extract()

        # Extract text
        text = soup.get_text(separator=" ")

        # Clean text
        cleaned_text = " ".join(text.split())

        # Limit size (VERY IMPORTANT for LLM)
        return cleaned_text[:5000]

    except Exception as e:
        return f"Error extracting content: {str(e)}"