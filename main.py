from pydantic_ai import Agent, ModelSettings

from dotenv import load_dotenv
load_dotenv()

from langfuse import get_client
langfuse = get_client()

agent = Agent(
    'openrouter:google/gemini-2.5-flash-lite',
    model_settings=ModelSettings(temperature=0.0),
    system_prompt=langfuse.get_prompt('basic').compile()
)

p = langfuse.get_prompt('beginner')
response = agent.run_sync('Do you know what will happen next week?')

with open('post.md', 'w') as f:
    f.write(response.output)