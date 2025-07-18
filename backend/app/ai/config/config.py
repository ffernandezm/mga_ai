import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
print(GOOGLE_API_KEY)
#OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") Cuando se tenga GPT