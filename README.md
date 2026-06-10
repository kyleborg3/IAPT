# XjenzaBot - IAPT
An LLM-Powered Private Chatbot for Xjenza Malta

<ins>Prerequisites</ins><br>
Before running XjenzaBot, make sure to have installed the following:<br>

1. **Ollama**  
   This can be installed from https://ollama.com. Then, pull the required models:
   ```bash
   ollama pull llama3
   ollama pull nomic-embed-text
   ```

2. **Python 3.11**
   Ensure that Python 3.11 is installed on your system.

<ins>Installation</ins><br>

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd chatbot
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   ```
   * **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   * **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

<ins>Adding Documents</ins><br>
Place your Xjenza Malta funding scheme PDF documents inside the `new_pdfs/` folder in the project root. XjenzaBot will automatically load, parse, and index them on startup.

<ins>Running the App</ins><br>
Make sure Ollama is running in the background, then launch the Streamlit app:
```bash
streamlit run main.py
```
Open your browser and navigate to the local URL displayed in your terminal (usually `http://localhost:8501`).

<ins>Usage</ins><br>
* Type your question in the input field at the bottom and press the send button.
* Speak your query by clicking the **Input Voice** button in the sidebar.
* Toggle **Enable Voice Output** in the sidebar to hear responses read aloud.
* Adjust **Voice Speed** as preferred.
* Click **Clear Chat** to reset the conversation.

<ins>Project Structure</ins><br>
```text
chatbot/
├── new_pdfs/           # Place your PDF documents here
├── main.py             # Main application entry point
├── requirements.txt    # Python dependencies
└── speech.mp3          # Temporary voice output file
```
   
