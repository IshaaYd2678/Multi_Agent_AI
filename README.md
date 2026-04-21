# ðŸ¤– Enhanced Multi-Agent AI Document Processing System

A powerful and advanced document processing application built with Python and Streamlit. This system leverages multiple AI agents to intelligently categorize, analyze, and extract insights from various document formats, including PDFs, JSONs, and Emails.

## ðŸŒŸ Key Features

- **ðŸ“„ Multi-Format Document Processing**: Supports parsing and analyzing PDF documents, JSON data, and Email (TXT) formats.
- **ðŸ§  AI Insights Engine**: Automatically generates smart tags, assesses risk levels, highlights action items, and evaluates sentiment.
- **âœ‰ï¸ Smart Reply Generation**: Suggests quick, context-aware reply templates for processed emails.
- **ðŸ“Š Analytics Dashboard**: Comprehensive statistics and visualizations showing document processing trends and metrics over time.
- **ðŸŒ Document Intelligence Network**: Advanced relationships mapping and risk analysis for the processed corpus.
- **ðŸ” Search & History**: Powerful search capabilities to quickly retrieve processed contexts using keywords, and filter history by format, intent, and urgency.
- **âš™ï¸ System Health Monitoring**: A built-in dashboard for checking system resource usage and component statuses.

## ðŸ› ï¸ Technology Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Data Visualization**: [Plotly](https://plotly.com/), [Pandas](https://pandas.pydata.org/)
- **AI Models**: OpenAI, Transformers, Torch
- **Document Extractors**: PyMuPDF (for PDF processing)
- **Environment Management**: python-dotenv

## ðŸ“ Project Structure

```text
.
â”œâ”€â”€ agents/                  # AI Agent modules 
â”‚   â”œâ”€â”€ classifier_agent.py  # Intent and format classification
â”‚   â”œâ”€â”€ email_agent.py       # Email parsing and analysis
â”‚   â”œâ”€â”€ insights_agent.py    # Generates smart tags, summaries, and action items
â”‚   â”œâ”€â”€ json_agent.py        # JSON structure validation and analysis
â”‚   â””â”€â”€ pdf_agent.py         # Extracts text and metadata from PDFs
â”œâ”€â”€ memory/                  # Shared memory / context management
â”‚   â””â”€â”€ shared_memory.py     # Implements context storage and retrieval
â”œâ”€â”€ utils/                   # Helper utilities
â”‚   â””â”€â”€ file_loader.py       # Reads and loads files (e.g., PyMuPDF wrappers)
â”œâ”€â”€ samples/                 # Sample documents for testing
â”œâ”€â”€ classifier.py            # Main classifier router
â”œâ”€â”€ main.py                  # CLI entry point to the system
â”œâ”€â”€ streamlit_app.py         # Main graphical interface (Streamlit App)
â””â”€â”€ requirements.txt         # Python dependencies
```

## ðŸš€ Installation

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

## ðŸŒ Deployment (Full Working App)

This project is a Streamlit app and is best deployed on container-based platforms (Render, Railway, Fly.io, etc.).

### Option A: Render (recommended)

1. Push this repository to GitHub.
2. In Render, create a **New Web Service** from this repo.
3. Render will detect `render.yaml` and `Dockerfile` automatically.
4. Add required environment variables in Render dashboard (`OPENAI_API_KEY`, etc.).
5. Deploy.

### Option B: Any Docker host

```bash
docker build -t multi-agent-ai .
docker run -p 8501:8501 --env-file .env multi-agent-ai
```

## ðŸ’» Usage

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

## ðŸ¤ Contribution

Contributions, issues, and feature requests are welcome! Feel free to modify the specific agents in the `agents/` folder to extend the AI capabilities of the system.
