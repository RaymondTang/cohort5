from pydantic_ai import Agent
from langfuse import get_client
from dotenv import load_dotenv
load_dotenv()
 
langfuse = get_client()
 
# Verify connection
if langfuse.auth_check():
    print("Langfuse client is authenticated and ready!")
    Agent.instrument_all()
else:
    print("Authentication failed. Please check your credentials and host.")

agent = Agent('openrouter:google/gemini-2.0-flash-lite-001')

prompt = langfuse.get_prompt("firstprompt")

r = agent.run_sync(prompt.compile(language="Traditional Chinese", position="Delivery Manager"))

print(r.output)