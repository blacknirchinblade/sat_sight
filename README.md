# 🛰️ Sat-Sight: AI-Powered Satellite Imagery Analysis# Sat-Sight: Advanced Agentic Satellite Image QA System



<div align="center">An intelligent multi-agent system for answering questions about satellite imagery using state-of-the-art AI techniques.



**An Advanced Multi-Agent System for Intelligent Satellite Imagery Analysis**## 🌟 Features



[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)### Multi-Agent Architecture

[![LangGraph](https://img.shields.io/badge/LangGraph-Powered-green.svg)](https://github.com/langchain-ai/langgraph)- **Planner Agent**: Intelligently routes queries based on type (image analysis, web search, general knowledge)

[![Streamlit](https://img.shields.io/badge/Streamlit-UI-red.svg)](https://streamlit.io/)- **Vision Agent**: Processes satellite images using CLIP embeddings and FAISS similarity search

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)- **Text Retrieval Agent**: Retrieves relevant knowledge from ChromaDB vector store

- **Web Search Agents**: Fetches real-time information via Tavily and DuckDuckGo

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Architecture](#-architecture) • [Documentation](#-documentation)- **Wikipedia Agent**: Provides encyclopedic context for topics

- **Reasoning Agent**: Synthesizes information from multiple sources into coherent responses

</div>- **Critic Agent**: Evaluates response quality and flags issues

- **Guardrail Agent**: Ensures safety and policy compliance

---- **Memory Agent**: Manages conversation history and user context

- **Geo Agent**: Handles location-based queries

## 📖 Overview- **Feedback Agent**: Processes user feedback for improvement

- **Coordinator Agent**: Orchestrates complex multi-step workflows

**Sat-Sight** is a cutting-edge multi-agent AI system designed to analyze satellite imagery and answer complex queries about Earth observation data. Built on **LangGraph**, it orchestrates 13 specialized AI agents that work together to provide comprehensive, accurate, and insightful responses.

### Intelligent Workflows

### What Makes Sat-Sight Unique?- **Text-Only Queries**: Routes directly to Wikipedia/Tavily without image processing

- **Image Analysis**: CLIP encoding → FAISS retrieval → Optional reranking

- 🧠 **Multi-Agent Intelligence**: 13 specialized agents collaborate seamlessly- **Contextual Analysis**: Combines image, text KB, and web search

- 👁️ **Visual Understanding**: CLIP-based image similarity search with 1050+ satellite images- **Multi-Source Synthesis**: Integrates multiple information sources

- 🌐 **Multi-Source Knowledge**: Combines vector databases, web search, and geographic data

- 💬 **Conversational Interface**: Natural language queries with multi-turn dialogue### Advanced Capabilities

- 🎯 **Adaptive Routing**: Smart query classification and dynamic agent coordination- **Hybrid LLM Routing**: Automatic fallback from Groq API to local Llama models

- 🔄 **Self-Improvement**: Critic and feedback loops ensure high-quality responses- **Memory Management**: Short-term, long-term, and episodic memory

- 💾 **Persistent Memory**: Episodic, short-term, and long-term memory systems- **Vector Search**: FAISS for images, ChromaDB for text

- **Response Reranking**: Cross-encoder models for relevance optimization

## ✨ Features- **Quality Control**: Automated response evaluation and revision loops



### Core Capabilities## 🏗️ Architecture



#### 🔍 Intelligent Query Processing```

- **Natural Language Understanding**: Ask questions in plain English┌─────────────┐

- **Multi-Modal Queries**: Text, image, or combined queries│   Query     │

- **Query Classification**: Automatic routing to appropriate agents└──────┬──────┘

- **Context Awareness**: Maintains conversation context across sessions       │

       v

#### 📸 Satellite Imagery Analysis┌─────────────────┐

- **Visual Similarity Search**: Find similar satellite images using CLIP│ Planner Agent   │ ← Classifies query type

- **1050+ Pre-indexed Images**: EuroSAT dataset with 10 land use classes└──────┬──────────┘

- **Metadata-Rich Results**: Class, location, coordinates, environmental context       │

- **Semantic Search**: Text-to-image and image-to-image search       ├─────────────┬─────────────┬──────────────┐

       │             │             │              │

#### 🌍 Geographic Intelligence       v             v             v              v

- **Coordinate Lookup**: Convert locations to GPS coordinates┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐

- **OpenStreetMap Integration**: Rich geographic data│ Vision   │  │   Text   │  │  Tavily  │  │Wikipedia │

- **Regional Analysis**: Country, continent, tile-based mapping│  Agent   │  │ Retrieval│  │  Search  │  │  Agent   │

- **Environmental Context**: Land use type, risks, features└────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘

     │             │             │              │

#### 🔗 Multi-Source Knowledge Integration     └─────────────┴─────────────┴──────────────┘

- **Vector Database**: Local knowledge base with ChromaDB                   │

- **Web Search**: Real-time information via Tavily API                   v

- **Wikipedia**: Structured factual knowledge            ┌─────────────┐

- **Memory Systems**: Learn from past interactions            │  Reasoning  │ ← Synthesizes info

            │    Agent    │

#### 💬 Advanced UI Features            └──────┬──────┘

- **Multi-Chat Sessions**: Manage multiple conversations                   │

- **Persistent History**: Chat data stored in SQLite                   v

- **Image Upload**: Analyze your own satellite images            ┌─────────────┐

- **Thinking Process Visualization**: See how agents reason            │   Critic    │ ← Evaluates quality

- **Responsive Design**: Works on desktop and mobile            │    Agent    │

- **Dark/Light Mode**: Automatic theme adaptation            └──────┬──────┘

                   │

## 🚀 Installation                   v

            ┌─────────────┐

### Prerequisites            │ Guardrail   │ ← Safety checks

            │    Agent    │

- **Python 3.12+** (recommended)            └──────┬──────┘

- **CUDA** (optional, for GPU acceleration)                   │

- **4GB+ RAM** (8GB+ recommended)                   v

- **5GB+ Disk Space**            ┌─────────────┐

            │  Response   │

### Quick Start            └─────────────┘

```

```bash

# Clone repository## 🚀 Setup

git clone https://github.com/yourusername/sat-sight.git

cd sat-sight### Prerequisites

- Python 3.8+

# Create environment- CUDA-capable GPU (recommended for local models)

conda create -n satsight python=3.12- 16GB+ RAM

conda activate satsight

### Installation

# Install dependencies

pip install -r requirements.txt```bash

# Clone repository

# Set up environment variablescd /home/ganesh/GenAi_Project/sat_sight

cp .env.example .env

# Edit .env with your API keys# Create virtual environment

python -m venv venv

# Run the applicationsource venv/bin/activate  # On Windows: venv\Scripts\activate

streamlit run ui/app_enhanced.py

```# Install dependencies

pip install -r requirements.txt

The application will open at `http://localhost:8501`

# Set up environment variables

### Environment Variablescp .env.example .env

# Edit .env with your API keys

Create a `.env` file:```



```bash### Environment Variables

# API Keys (comma-separated for fallback)

GROQ_API_KEYS="key1,key2,key3"Create a `.env` file with:

TAVILY_API_KEY="your_tavily_key"

```bash

# Optional Settings# Required

DEBUG=FalseGROQ_API_KEY=your_groq_api_key_here

USE_LOCAL_ONLY=False  # Use only local modelsTAVILY_API_KEY=your_tavily_api_key_here

```

# Optional

## 💻 UsageLOCAL_LLM_PATH=data/models/Phi-3-mini-4k-instruct-q4.gguf

DEBUG=False

### Example Queries```



#### Image Search### Data Setup

```

show me forest images```bash

find deforested areas# Download and prepare satellite images

display urban sprawl examplespython scripts/ingest_satellite_data.py

show agricultural land in India

```# Build FAISS index for images

python utils/build_image_index.py

#### Knowledge Queries

```# Index text documents in ChromaDB

what is deforestation and its impacts?python retrieval/chroma_manager.py --ingest data/text_docs/

explain urban heat island effect```

how do satellites detect water pollution?

tell me about Sentinel-2 satellite## 📖 Usage

```

### Python API

#### Location Queries

``````python

what are the coordinates of Paris?from sat_sight.core.workflow import run_workflow

find forests near the Amazon basin

show me urban areas in Europe# Example 1: Image analysis

locate rivers in Switzerlandresponse, state = run_workflow(

```    query="What type of land cover is shown in this image?",

    image_path="data/images/forest_area.jpg",

#### Multi-Modal Queries    user_id="user123"

```)

[Upload image] + "what type of land use is this?"print(response)

[Upload image] + "find similar satellite images"

show me crop images and explain crop rotation# Example 2: General knowledge (no image)

```response, state = run_workflow(

    query="What is deforestation and why is it concerning?",

### Web Interface Features    image_path="",

    user_id="user123"

1. **Multi-Chat Management**)

   - Create multiple chat sessionsprint(response)

   - Switch between conversations

   - Persistent across page refreshes# Example 3: Web search

   - Search and filter chatsresponse, state = run_workflow(

    query="What are the latest developments in satellite monitoring?",

2. **Image Upload**    image_path="",

   - Upload your own satellite images    user_id="user123"

   - Analyze and find similar images)

   - Visual similarity searchprint(response)

```

3. **Thinking Process**

   - See how agents collaborate### Web UI

   - Understand decision-making

   - Track data sources used```bash

cd ui

4. **Session Persistence**./run_ui.sh

   - Chat history stored in SQLite# Or: streamlit run app.py

   - No data loss on refresh```

   - Export conversation history

Navigate to `http://localhost:8501`

## 🏗️ Architecture

### CLI

### System Overview

```bash

```python -m sat_sight.core.workflow --query "Analyze this forest" --image data/images/forest.jpg

┌──────────────────────────────────────────────────────────────┐```

│                     User Interface Layer                      │

│                    (Streamlit Web App)                        │## 🎯 Query Types

└────────────────────────────┬─────────────────────────────────┘

                             │### Supported Query Categories

┌────────────────────────────▼─────────────────────────────────┐

│                    LangGraph Workflow                         │1. **General Knowledge**: "What is deforestation?"

│                 (State Machine Orchestration)                 │   - Routes to: Wikipedia → Reasoning

└─┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬─────────┘   

  │      │      │      │      │      │      │      │2. **Image Analysis**: "What's in this image?"

  ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼   - Routes to: Vision → Reasoning

┌────┐┌────┐┌─────┐┌────┐┌──────┐┌──────┐┌─────┐┌──────┐   

│Plan││Vis.││Text ││Geo ││Search││Reason││Critic││Memory│3. **Contextual Analysis**: "Is this forest at risk?"

│ner ││Agt.││ KB  ││Agt.││Agents││ Agt. ││ Agt. ││ Agt. │   - Routes to: Vision → Text Retrieval → Web Search → Reasoning

└─┬──┘└─┬──┘└──┬──┘└─┬──┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘   

  │     │      │     │      │       │       │       │4. **Web Search**: "Latest news about Amazon deforestation"

  ▼     ▼      ▼     ▼      ▼       ▼       ▼       ▼   - Routes to: Tavily Search → Reasoning

┌─────┐┌────┐┌─────┐┌────┐┌─────┐┌─────┐┌──────┐┌──────┐   

│FAISS││CLIP││Chroma││OSM ││Tavily││Groq ││SQLite││Memory│5. **Location Queries**: "Show data for coordinates 40.7, -74.0"

│Index││ AI ││  DB  ││    ││ API ││ API ││  DB  ││Store │   - Routes to: Geo Agent → Reasoning

└─────┘└────┘└─────┘└────┘└─────┘└─────┘└──────┘└──────┘

```## 🧠 Prompt Engineering



### Agent Workflow### Planner Prompts

- Structured JSON classification

See how agents collaborate to answer queries:- Category detection with confidence scores

- Multi-source need assessment

1. **Planner** classifies query type (image/text/web/location)

2. **Specialized Agents** retrieve relevant data from their sources### Reasoning Prompts

3. **Coordinator** orchestrates multi-source queries- Clear source acknowledgment

4. **Reasoning Agent** synthesizes information and generates response- Structured synthesis instructions

5. **Critic Agent** evaluates quality and triggers improvement if needed- Citation requirements

6. **Memory Agent** stores context for future queries- Conflict resolution guidelines

7. **Guardrail Agent** ensures content safety

### Critic Prompts

### 13 Specialized Agents- Multi-criteria evaluation

- Scoring rubrics (relevance, accuracy, clarity)

| Agent | Purpose | Data Source |- Revision flagging logic

|-------|---------|-------------|

| Planner | Query classification & routing | Rule-based + LLM |## 📊 Evaluation

| Vision | Image similarity search | FAISS + CLIP |

| Text Retrieval | Document search | ChromaDB |Run evaluation scripts:

| Geo | Location & coordinates | OpenStreetMap |

| Tavily Search | Premium web search | Tavily API |```bash

| Wikipedia | Structured knowledge | Wikipedia API |python evaluation/evaluate.py --dataset evaluation/test_dataset.json

| Search | General web search | DuckDuckGo |```

| Coordinator | Multi-source orchestration | State management |

| Reasoning | Response synthesis | Groq API + Local |Metrics tracked:

| Critic | Quality evaluation | LLM-based scoring |- F1 Score

| Feedback | Iterative improvement | Multi-iteration |- Exact Match (EM)

| Memory | Context management | Custom stores |- BLEU Score

| Guardrail | Content safety | Rule-based filters |- Response Time

- Confidence Scores

## 📚 Documentation

## 🔧 Configuration

### Core Documentation

Edit `core/config.py`:

- **[Architecture Overview](docs/architecture/ARCHITECTURE.md)** - System design and data flow

- **[Agent Documentation](docs/agents/README.md)** - Detailed agent specifications```python

- **[Memory Systems](docs/memory/README.md)** - Episodic, STM, and LTM design# Model Configuration

API_MODEL_NAME = "llama-3.3-70b-versatile"

### Individual Agent DocsLOCAL_LLM_PATH = "data/models/your_model.gguf"



- [Vision Agent](docs/agents/vision_agent.md) - Image similarity search with CLIP# Retrieval Configuration

- [Reasoning Agent](docs/agents/reasoning_agent.md) - LLM-powered synthesisFAISS_RETRIEVAL_K = 5

- [Planner Agent](docs/agents/planner_agent.md) - Query classificationCHROMA_RETRIEVAL_K = 5

- [Full Agent List](docs/agents/README.md)RERANK_TOP_K = 3



## 🗺️ Roadmap# Memory Configuration

STM_SIZE = 5  # conversation turns

### Current Version: 2.0 ✅```



- ✅ Multi-agent LangGraph architecture## 🗂️ Project Structure

- ✅ CLIP-based visual search

- ✅ Multi-chat Streamlit UI```

- ✅ Persistent memory systemssat_sight/

- ✅ API fallback mechanisms├── agents/           # Agent implementations

│   ├── planner.py

### Version 2.1 (Q1 2025)│   ├── vision_agent.py

│   ├── reasoning_agent.py

- [ ] Real-time satellite data APIs (NASA, Sentinel Hub)│   ├── critic_agent.py

- [ ] Advanced change detection over time│   └── ...

- [ ] Multi-image temporal analysis├── core/             # Core framework

- [ ] Enhanced mobile UI│   ├── state.py

- [ ] Performance optimizations│   ├── workflow.py

│   └── config.py

### Version 2.2 (Q2 2025)├── retrieval/        # Retrieval modules

│   ├── clip_encoder.py

- [ ] REST API with FastAPI│   ├── faiss_manager.py

- [ ] WebSocket streaming responses│   ├── chroma_manager.py

- [ ] Multi-user authentication│   └── reranker.py

- [ ] Cloud deployment templates├── models/           # LLM routing

- [ ] Docker containerization│   ├── llm_router.py

│   └── embedding.py

### Version 3.0 (Q3 2025)├── tools/            # External tools

│   ├── satellite_api.py

- [ ] Fine-tuned CLIP for satellite imagery│   └── tavily_search_wrapper.py

- [ ] Custom object detection models├── ui/               # Web interface

- [ ] Predictive analytics and forecasting│   └── app.py

- [ ] Export to GIS formats (GeoJSON, Shapefile)├── evaluation/       # Testing & metrics

- [ ] Integration with QGIS│   └── evaluate.py

└── data/             # Data storage

## 🤝 Contributing    ├── images/

    ├── text_docs/

We welcome contributions! Here's how:    └── vector_stores/

```

1. Fork the repository

2. Create a feature branch (`git checkout -b feature/amazing-feature`)## 🐛 Troubleshooting

3. Make your changes with tests

4. Submit a pull request### Common Issues



See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.**1. FAISS Index Not Found**

```bash

## 📊 Datasetpython utils/build_image_index.py

```

**EuroSAT Dataset** (Included)

**2. ChromaDB Collection Empty**

- **Images**: 1050 satellite images```bash

- **Classes**: 10 land use types (Annual Crop, Forest, Urban, etc.)python retrieval/chroma_manager.py --ingest data/text_docs/

- **Source**: Sentinel-2 satellite```

- **Resolution**: 64x64 pixels (RGB)

- **Coverage**: Europe (Switzerland, Austria, Germany, Poland, Czech Republic)**3. Groq API Rate Limiting**

- System automatically falls back to local model

## 🙏 Acknowledgments- Adjust `USE_LOCAL_FALLBACK = True` in config



- **LangGraph** - Multi-agent orchestration**4. Out of Memory**

- **OpenAI CLIP** - Vision-language understanding- Reduce `FAISS_RETRIEVAL_K` and `CHROMA_RETRIEVAL_K`

- **EuroSAT** - Satellite imagery dataset- Use smaller local model

- **Streamlit** - Interactive web UI- Disable reranking

- **Groq** - Fast LLM inference

- **Tavily** - Web search API## 📝 Contributing



## 📄 License1. Fork the repository

2. Create feature branch (`git checkout -b feature/AmazingFeature`)

MIT License - see [LICENSE](LICENSE) file for details.3. Commit changes (`git commit -m 'Add AmazingFeature'`)

4. Push to branch (`git push origin feature/AmazingFeature`)

## 📧 Contact5. Open Pull Request



**Project**: Sat-Sight Multi-Agent System## 📜 License



- GitHub Issues: [Report bugs or request features](https://github.com/yourusername/sat-sight/issues)MIT License - see LICENSE file

- Discussions: [Join the community](https://github.com/yourusername/sat-sight/discussions)

## 🙏 Acknowledgments

---

- CLIP by OpenAI

<div align="center">- FAISS by Facebook Research

- ChromaDB by Chroma

**Built with ❤️ for Earth Observation and AI**- LangGraph by LangChain

- Groq for fast LLM inference

⭐ **Star this repo if you find it useful!** ⭐

## 📞 Support

</div>

- Issues: [GitHub Issues](https://github.com/yourusername/sat_sight/issues)
- Email: support@satsight.ai
- Docs: [Full Documentation](https://docs.satsight.ai)

## 🎯 Roadmap

- [ ] Support for temporal image comparisons
- [ ] Integration with more satellite data APIs
- [ ] Fine-tuned reranking models
- [ ] Multi-language support
- [ ] Enhanced memory persistence
- [ ] Real-time streaming responses

---

**Built with ❤️ for environmental monitoring and satellite intelligence.**
