# 🎬 AI-Powered Netflix & Streaming Availability Assistant

**Author:** Adi Meller

## 📋 System Overview
This project is an intelligent media assistant integrated within **Open Web UI**. By combining **Retrieval-Augmented Generation (RAG)** with **Agentic Tool Calling**. designed to bridge the gap between static historical data and real-time streaming availability. By unifying a custom knowledge base with live API-driven tools, the system transforms a standard chatbot into a context-aware media expert, capable of solving two core limitations of Large Language Models (LLMs): the lack of real-time data and the tendency to hallucinate factual details.

---

## 🏗️ System Architecture & Core Components How it works

The assistant operates through three integrated components working in synergy within the Open Web UI environment:

### 1. The RAG Pipeline: Knowledge Base (Inside Web UI)

- **Data Source:** "Netflix Movies and TV Shows" dataset sourced from Kaggle (`netflix_titles.csv`).
- **Implementation:** The static CSV file is uploaded and natively indexed as a Knowledge Base within Open Web UI. The data is chunked and stored in an internal Vector Database.
- **Role:** Acts as the system's "long-term memory." When queried about directors, cast members, release years, or show synopses, the LLM performs a semantic search against this dataset, retrieving exact excerpts (Sources) to ground its answers in factual data without requiring external API calls.

<img width="903" height="341" alt="image" src="https://github.com/user-attachments/assets/f58b1374-121a-487f-857c-424c8e296238" />

### 2. The Proxy Backend: Local Python Server (`tools_server.py`)

- **Technology Stack:** Python, Flask, `requests` library, `python-dotenv`.
- **External Integration:** RapidAPI "Streaming Availability" (by Movie of the Night).
- **Network & Port Configuration:** The server is deliberately configured to run on `host="0.0.0.0"` and `port=5005`. Binding to `0.0.0.0` is a critical architectural decision; it ensures the Flask server is exposed to the local network interfaces, allowing the Open Web UI (which operates isolated inside a Docker container) to successfully route HTTP requests to the host machine via `http://host.docker.internal:5005`.
- **Data Flow & Token Optimization (Why we built this):**
  LLMs struggle with parsing massive, unfiltered JSON payloads. Instead of allowing the Web UI to directly query RapidAPI, this Flask server acts as a middleware proxy.
  1. It receives a targeted GET request (e.g., `?title=Breaking Bad&country=il`).
  2. It securely injects the RapidAPI authentication keys (hiding them from the frontend).
  3. It executes the query, receives a massive data payload, and performs strict data parsing.
  4. It extracts only the essential data points: Service Name, Stream Type (Subscription/Rent/Buy), and Direct Viewing Links.
  5. It returns a lightweight, sanitized JSON response back to the Web UI, significantly reducing token consumption and preventing LLM context-window overload.

### 3. Agentic Orchestration: Web UI Tool

- **Implementation:** A custom Python tool declared within the Open Web UI workspace.
- **Role:** This component acts as the "bridge." Through precise docstrings and type hinting, the LLM is granted agency to autonomously decide _when_ to use this tool. If a user asks a real-time question (e.g., _"Where can I stream this show in Israel today?"_), the LLM intercepts the prompt, extracts the relevant parameters, triggers the local Flask server, and seamlessly weaves the retrieved JSON data into a natural language response.
- **Architectural Decision: Why a Tool instead of a Function (Filter)?**
  - **Agentic Routing:** A Function executes blindly on every prompt, wasting resources and API calls. A Tool empowers the LLM with decision-making autonomy, allowing it to intelligently route queries to the live API only when necessary.
  - **NLP over Regex:** Extracting complex movie titles (e.g., "The 40-Year-Old Virgin") using hardcoded Regular Expressions is brittle and error-prone. Tools leverage the LLM's native Natural Language Processing to extract exact parameters seamlessly.
  - **Scalability:** This design is highly extensible. Adding new features (like IMDb reviews or ticket booking) simply requires registering additional Tools, positioning the LLM as a true orchestration engine.
 
<img width="1912" height="1069" alt="Streaming_Availability_Tool_1" src="https://github.com/user-attachments/assets/b9909c5a-1fdb-470b-8bd8-1e1eb1ea218c" />

<img width="1911" height="1064" alt="Streaming_Availability_Tool_2" src="https://github.com/user-attachments/assets/733be100-7537-4ee2-b9d4-70f0a43dd121" />

---


<img width="1902" height="1006" alt="TEST_streaming_availability_tool_1" src="https://github.com/user-attachments/assets/1906ff11-5788-4c6b-be5b-57b7bf983014" />

<img width="1908" height="994" alt="TEST_streaming_availability_tool_2" src="https://github.com/user-attachments/assets/4137d3e3-7e34-40eb-bc2c-9b5cf546b103" />

<img width="1608" height="998" alt="TEST_streaming_availability_tool_3" src="https://github.com/user-attachments/assets/4efbeba5-4616-4d29-b232-c0e33b81b380" />



## Summary
This project demonstrates how to extend a standard Open Web UI setup by integrating personal datasets and custom backend services. By orchestrating these components, the system functions as a robust, agentic engine that is both knowledgeable about media history and connected to the pulse of live streaming platforms.

## 🚀 Installation & Execution

To run the local backend server and test the integration:

1. **Environment Setup:**
   Ensure you have a virtual environment (`venv`) active. Install the required dependencies:
   ```bash
   pip install flask requests
   ```

## Configure API Keys:

Open tools_server.py and replace YOUR_RAPIDAPI_KEY_HERE with your active RapidAPI key.

Run the Proxy Server:
Execute the server script from your terminal:

python tools_server.py

Expected output: The console will indicate the server is running on http://0.0.0.0:5005/.

Standalone API Testing:
Before querying the LLM, verify the server works by navigating to the following URL in your browser:
http://localhost:5005/streaming_status?title=stranger%20things&country=us
You should see a clean JSON response detailing where the show is currently streaming.

📸 Testing & Verification Screenshots
(Add your visual proof here to demonstrate system functionality)

1. Knowledge Base (RAG) Validation:
   Demonstrating the LLM correctly pulling cast/director information directly from the uploaded CSV.

``

2. Local Server JSON Response:
   Proof of the Flask server successfully parsing the RapidAPI data via browser or Postman.

``

3. End-to-End Tool Calling:
   The final integration showing the LLM answering a mixed prompt by utilizing both the RAG database and the live Streaming Tool.

``
