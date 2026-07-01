import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"


def get_llm_response(prompt: str) -> str:
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
            },
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()
        return data.get("response", "").strip()

    except requests.exceptions.RequestException:
        return "ಉತ್ತರವನ್ನು ಸಿದ್ಧಪಡಿಸಲು ಸ್ವಲ್ಪ ಹೆಚ್ಚು ಸಮಯ ತೆಗೆದುಕೊಳ್ಳುತ್ತಿದೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."
