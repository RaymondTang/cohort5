# Venturenix Next-Gen AI Development Class Cohort #5

### 1. Pick the Right LLMs

Understanding today’s model landscape and when to use each category:

#### Base (Raw) LLMs
- **What**: Foundation models without task-specific fine-tuning
- **When**: Maximum control, custom fine-tunes, research
- **Examples**: Llama 3.2 Base, Qwen2.5 Base

#### Instruction-Tuned LLMs
- **What**: Fine-tuned to follow instructions reliably
- **When**: General tasks, tools, agents with predictable adherence
- **Examples**: Claude 3 Opus, Gemini 2.0

#### Chat-Optimized LLMs
- **What**: Tuned for multi-turn dialogue and safety
- **When**: Chatbots, support, assistants
- **Examples**: GPT-4o Mini, Claude 3 Haiku

#### Code LLMs
- **What**: Trained heavily on code and repos
- **When**: Code generation, refactors, unit tests, migrations
- **Examples**: Claude Sonnet

#### Multimodal LLMs
- **What**: Understand text + images (+ audio/video in some)
- **When**: Screenshots, documents, diagrams, UI flows, OCR
- **Examples**: Gemini 2.5 series

#### Reasoning Models
- **What**: Optimized for planning and complex multi-step problems
- **When**: Analysis, tool-using agents, math/logic, RAG planning
- **Examples**: OpenAI o3, DeepSeek R1

#### Small Language Models (SLMs)
- **What**: Compact models for cost/latency or on-device
- **When**: Edge, offline, PII-bound, high QPS, low-latency
- **Examples**: Phi-3.5 Mini, Gemma 3

### 2. What is Prompt Engineering?

Prompt engineering is the practice of designing and optimizing input prompts to get the best possible output from language models. It involves crafting clear, specific instructions that guide the AI to produce desired results.

#### 2.1 Key Components of a Prompt

##### Instruction
- **Purpose**: Tells the AI what task to perform
- **Example**: "Write a professional email"
- **Best practices**: Be specific and clear about the desired action

##### Context
- **Purpose**: Provides background information to help the AI understand the situation
- **Example**: "You are a customer service representative for a tech company"
- **Best practices**: Include relevant details that affect the output

##### Question
- **Purpose**: The specific query or request you want answered
- **Example**: "How do I reset my password?"
- **Best practices**: Be direct and specific about what you need

##### Example
- **Purpose**: Shows the AI the format or style you want
- **Example**: Providing a sample email format
- **Best practices**: Use clear, representative examples

##### Output Format
- **Purpose**: Specifies how you want the response structured
- **Example**: "Respond in JSON format with fields: subject, body, signature"
- **Best practices**: Be explicit about formatting requirements

### 2.2 [Advanced Prompting Techniques](https://www.promptingguide.ai/techniques)

- **Chain-of-Thought (CoT)**: Breaking down complex problems into smaller, manageable steps.
- **ReAct**: Combining reasoning and action to solve problems.
- **Few-Shot Prompting**: Providing examples of desired outputs to guide the model.

### 3. n8n Hands-on Lab

Practical exercises using n8n for workflow automation and AI integration.

### 4. What is Context Engineering?

Context engineering focuses on managing and optimizing the information that influences an AI model's responses. It goes beyond individual prompts to consider the broader context that shapes AI behavior.

#### How Context Engineering is Different from Prompt Engineering

- **Scope**: Context engineering considers the entire conversation history and system context, while prompt engineering focuses on individual input optimization
- **Persistence**: Context engineering manages information that persists across multiple interactions, while prompt engineering is typically single-interaction focused
- **Strategy**: Context engineering involves strategic information management, while prompt engineering is more tactical
- **Long-term thinking**: Context engineering considers how information builds up over time, while prompt engineering optimizes for immediate results

#### Key Concepts from "Context Engineering for Agents"

- **Link**: [Context Engineering for Agents by Lance Martin](https://rlancemartin.github.io/2025/06/23/context_engineering/)
- **Core Idea**: The art and science of filling the context window with just the right information at each step of an agent’s trajectory.
- **Key Strategies**:
    - **Write Context**: Saving information outside the context window (e.g., scratchpads, memories).
    - **Select Context**: Pulling relevant information into the context window (e.g., from scratchpads, memories, tools, or knowledge bases via RAG).
    - **Compress Context**: Summarizing or trimming context to retain only essential tokens.
    - **Isolate Context**: Splitting context across multiple agents or environments to manage complexity.

https://learnprompting.org/docs/introduction