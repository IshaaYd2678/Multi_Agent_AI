# 🤖 Enhanced Multi-Agent AI Document Processing System

A powerful and advanced document processing application built with Python and Streamlit. This system leverages multiple AI agents to intelligently categorize, analyze, and extract insights from various document formats, including PDFs, JSONs, and Emails.

## 🌟 Key Features

- **📄 Multi-Format Document Processing**: Supports parsing and analyzing PDF documents, JSON data, and Email (TXT) formats.
- **🧠 AI Insights Engine**: Automatically generates smart tags, assesses risk levels, highlights action items, and evaluates sentiment.
- **✉️ Smart Reply Generation**: Suggests quick, context-aware reply templates for processed emails.
- **📊 Analytics Dashboard**: Comprehensive statistics and visualizations showing document processing trends and metrics over time.
- **🌐 Document Intelligence Network**: Advanced relationships mapping and risk analysis for the processed corpus.
- **🔍 Search & History**: Powerful search capabilities to quickly retrieve processed contexts using keywords, and filter history by format, intent, and urgency.
- **⚙️ System Health Monitoring**: A built-in dashboard for checking system resource usage and component statuses.

## 🛠️ Technology Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Data Visualization**: [Plotly](https://plotly.com/), [Pandas](https://pandas.pydata.org/)
- **AI Models**: OpenAI, Transformers, Torch
- **Document Extractors**: PyMuPDF (for PDF processing)
- **Environment Management**: python-dotenv

## 📁 Project Structure

```text
.
├── agents/                  # AI Agent modules 
│   ├── classifier_agent.py  # Intent and format classification
│   ├── email_agent.py       # Email parsing and analysis
│   ├── insights_agent.py    # Generates smart tags, summaries, and action items
│   ├── json_agent.py        # JSON structure validation and analysis
│   └── pdf_agent.py         # Extracts text and metadata from PDFs
├── memory/                  # Shared memory / context management
│   └── shared_memory.py     # Implements context storage and retrieval
├── utils/                   # Helper utilities
│   └── file_loader.py       # Reads and loads files (e.g., PyMuPDF wrappers)
├── samples/                 # Sample documents for testing
├── classifier.py            # Main classifier router
├── main.py                  # CLI entry point to the system
├── streamlit_app.py         # Main graphical interface (Streamlit App)
└── requirements.txt         # Python dependencies
```

## 🚀 Installation

1. **Clone the repository** (if applicable) or navigate to the project directory:
   ```bash
   cd Multi_agent_AI
   ```

2. **Create a virtual environment (optional but recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Create a `.env` file in the root directory and add any necessary API keys (like `OPENAI_API_KEY`).

## 💻 Usage

### Web Interface (Streamlit)

To launch the insightful graphical user interface, simply run:

```bash
streamlit run streamlit_app.py
```

Use the sidebar to explore the main processing tool, analytics dashboard, search history, and AI insights.

### Command Line Interface (CLI)

To test the multi-agent AI pipeline headlessly:

```bash
python main.py
```

This processes the sample documents located in the `samples/` directory and outputs the multi-agent reasoning trace and analytics directly parsing results to your terminal.

## 🤝 Contribution

Contributions, issues, and feature requests are welcome! Feel free to modify the specific agents in the `agents/` folder to extend the AI capabilities of the system.
