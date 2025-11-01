# genai

Nathan Verrill

2025

## experiments

Overall setup

- litellm
- ollamma on local (bare metal; not docker; optimized for apple silicon gpu; 2 simultaneous models)
- openai through aws bedrock
- crewai
- arize phoenix
- phoenix notebooks: https://github.com/Arize-ai/phoenix

### tokens

token optimization strategies

- remove vs local
- ollama, multiple models installed, m1, 32gb unified memory
- comparing models
- dropping prompt words
- strategic synonyms
- strategic typos
- devoweling / selective devoweling
- summarize / shorten prompt with local llm before sending?
- context management
- cached

when testing

- turn off streaming
- turn off memory so context isn't maintained

### security

abac/rbac

- store agent, tool, task definitions in db with security tags
- keycloak configed with access controls; security tags passed through AI when models are instantiated

### gotchas

- crewai, needing to specify project name in each crew.py when just copying over another crew.py
- run litellm external with same model list (or maybe can get model lsit from litellm and just run from there?)
- updating toml when grabbing requirements.txt; keeping a run() method in scripts; resolving config paths
- use ChatLiteLLM and not the OpenAI version, even if it's an OpenAI compatible custom api
