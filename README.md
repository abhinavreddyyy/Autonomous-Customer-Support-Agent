# Autonomous Customer Support Agent

A production-ready customer support agent built with LangChain, OpenAI API, and FAISS. Uses the ReAct framework for transparent reasoning and tool usage.

## Features

- **ReAct Framework**: Reasoning + Acting approach for transparent agent behavior
- **RAG Pipeline**: FAISS-based semantic search over product catalog and FAQ
- **Persistent Memory**: Conversation history and user preferences across sessions
- **Multi-Tool Support**: Order lookup, ticket creation, pricing info, shipping calculation
- **Agent Evaluation**: Built-in testing and performance metrics
- **Production Ready**: Logging, error handling, configuration management

## Project Structure

```
autonomous-support-agent/
├── config/                 # Configuration management
│   ├── __init__.py
│   └── settings.py        # Pydantic settings with environment variables
│
├── data/                  # Data files
│   ├── product_catalog.json
│   ├── faq_data.json
│   └── memory/           # User conversation history
│
├── rag/                   # Retrieval-Augmented Generation
│   ├── __init__.py
│   ├── vector_store.py   # FAISS index and embeddings
│   └── faiss_retriever.py # LangChain retrieval tools
│
├── memory/               # Conversation memory management
│   ├── __init__.py
│   └── persistent_memory.py
│
├── tools/                # Custom agent tools
│   ├── __init__.py
│   └── custom_tools.py  # Order lookup, tickets, pricing, shipping
│
├── agent/               # Agent implementation
│   ├── __init__.py
│   ├── react_agent.py  # Main ReAct agent
│   └── prompts.py      # System prompts and instructions
│
├── evaluation/          # Agent evaluation
│   ├── __init__.py
│   └── evaluate_agent.py
│
├── tests/              # Unit tests
│   ├── __init__.py
│   ├── test_vector_store.py
│   └── test_agent.py
│
├── main.py             # Interactive CLI interface
├── evaluation_script.py # Run agent evaluation
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variable template
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## Installation

1. **Clone/Download the project**
```bash
cd autonomous-support-agent
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables**
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

## Quick Start

### Interactive Mode
```bash
python main.py
```

### Demo Mode
```bash
python main.py demo
```

### Run Evaluation
```bash
python evaluation_script.py
```

### Run Tests
```bash
pytest tests/
```

## Configuration

Edit `.env` file with your settings:

```ini
# OpenAI Configuration
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# FAISS Configuration
FAISS_INDEX_PATH=./data/faiss_index
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Agent Configuration
MAX_ITERATIONS=10
TIMEOUT_SECONDS=30
TOP_K_RESULTS=3
SIMILARITY_THRESHOLD=0.5
```

## Component Details

### 1. Vector Store (RAG)
- Loads product catalog and FAQ data
- Uses sentence-transformers for embeddings
- FAISS for semantic search
- Similarity filtering

### 2. Agent Tools
- **semantic_search**: Search knowledge base
- **product_search**: Find products
- **faq_search**: Search FAQs
- **order_lookup**: Look up orders
- **pricing_info**: Get pricing/promotions
- **calculate_shipping**: Estimate shipping
- **create_support_ticket**: Create tickets

### 3. Memory Management
- ConversationBufferWindowMemory
- Persistent user preferences
- Conversation history on disk
- Per-user session management

### 4. Agent (ReAct Framework)
- Structured reasoning
- Tool-use documentation
- Error handling
- Multi-turn conversations

## Usage Examples

### Python API
```python
from agent.react_agent import get_react_agent

agent = get_react_agent(user_id="user123")
response, metadata = agent.process_input("What's the price of headphones?")
print(response)
```

### Interactive Chat
```bash
python main.py
```

### Running Evaluation
```python
from evaluation.evaluate_agent import AgentEvaluator

evaluator = AgentEvaluator()
results = evaluator.run_full_evaluation()
evaluator.print_summary()
evaluator.save_results()
```

## Agent Flow

1. **Input**: User query received
2. **Memory**: Conversation history loaded
3. **Reasoning**: ReAct framework analyzes query
4. **Tool Selection**: Choose appropriate tools
5. **Tool Use**: Execute tools to gather information
6. **Response Generation**: Formulate answer
7. **Memory Update**: Save to conversation history

## Performance Metrics

The evaluation system tracks:
- **Accuracy**: Presence of expected keywords
- **Hallucination**: Detection of made-up information
- **Relevance**: Response appropriateness to query
- **Overall Score**: Composite metric

## Extending the Agent

### Add Custom Tool
```python
from langchain.tools import BaseTool

class MyTool(BaseTool):
    name = "my_tool"
    description = "What this tool does"
    
    def _run(self, input_str: str) -> str:
        # Implementation
        return "result"
    
    async def _arun(self, input_str: str) -> str:
        return self._run(input_str)
```

### Add Product Data
Edit `data/product_catalog.json` with new products.

### Modify System Prompt
Edit agent prompts in `agent/prompts.py`

## Troubleshooting

**FAISS Index Not Found**: Run initialization to create index
```python
from rag.vector_store import get_vector_store
vs = get_vector_store()
```

**OpenAI API Error**: Check .env has valid OPENAI_API_KEY

**Memory Not Persisting**: Ensure data/memory/ directory exists

## License

MIT License

## Support

For issues or questions, create a GitHub issue or support ticket through the agent.# Autonomous-Customer-Support-Agent
