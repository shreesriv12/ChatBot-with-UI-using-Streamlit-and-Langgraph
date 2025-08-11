# LangGraph Chatbot with Flask and HTML/JS

This project is a full-stack, real-time chatbot application. The backend is built with Python Flask and LangGraph, using Google's Gemini 1.5 Flash model for conversational AI. The frontend is a single-page application using vanilla HTML, CSS, and JavaScript.

The application provides a seamless chat experience with conversation history, a clean UI with dark/light mode, and real-time streaming of AI responses.

## 🚀 Features

- **Real-time Chat**: Get streaming responses from the AI for a dynamic user experience.
- **Conversation History**: All chats are saved to an SQLite database using LangGraph's SqliteSaver checkpointer.
- **New Chat Functionality**: Easily start a fresh conversation at any time.
- **Persistent Threads**: Click on a past conversation to instantly load the full chat history.
- **Responsive UI**: A modern, responsive design that works on both desktop and mobile.
- **Dark/Light Mode**: Toggle between light and dark themes for comfortable viewing.
- **Markdown Formatting**: The assistant's responses are rendered with basic markdown support (bold, italic, lists, code blocks).
- **Flask Backend**: A lightweight and efficient API to handle chat logic and state management.

## 🛠️ Tech Stack

### Backend:
- **Python**: The core language.
- **Flask**: A micro-framework for building the web server and API endpoints.
- **LangGraph**: A library for building robust, stateful LLM applications.
- **langchain-google-genai**: The LangChain integration for connecting to Google's Gemini models.
- **SQLite**: A lightweight, file-based database for storing chat history.
- **python-dotenv**: For securely managing API keys and environment variables.

### Frontend:
- **HTML**: The structure of the web page.
- **CSS**: Styling, including a responsive design and smooth animations.
- **JavaScript**: Handles all frontend logic, including API calls, DOM manipulation, and UI interactions.

## 📝 Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2. Set up a virtual environment

It's highly recommended to use a virtual environment to manage project dependencies.

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

Install the required Python packages from the requirements.txt file.

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

Create a file named `.env` in the root directory of the project and add your Google API Key. You can get a key from Google AI Studio.

```bash
GOOGLE_API_KEY="your_api_key_here"
```

### 5. Create the index.html file

The Flask app uses `render_template('index.html')`, so you need to create a templates directory and place the provided HTML code inside it.

```bash
# Create the templates folder
mkdir templates

# Create the index.html file inside the templates folder
# Paste the provided HTML code into this new file
touch templates/index.html 
```

### 6. Run the Flask application

You can now start the application from your terminal.

```bash
python app.py
```

The application will be running on `http://localhost:5000`. Open this URL in your web browser to start chatting!

## 💡 How it Works

### Frontend (HTML/JS):
- A simple HTML page with a sidebar for threads and a main chat area.
- JavaScript handles all communication with the Flask backend.
- When a user sends a message, a POST request is sent to `/api/chat`.
- The UI updates dynamically, showing user messages immediately and an animated "typing" indicator while waiting for the AI's response.
- The `chat_stream` endpoint uses Server-Sent Events (SSE) for a more efficient and real-time streaming experience.

### Backend (Flask/LangGraph):
- The Flask app defines several API endpoints to manage threads and handle chat interactions.
- A LangGraph StateGraph is used to create the conversational agent. The ChatState defines a list of messages.
- The `chat_node` takes the current list of messages, invokes the Gemini 1.5 Flash model, and returns the new message to the state.
- The SqliteSaver checkpointer automatically saves the state (the full conversation history) to `chatbot.db` with a unique `thread_id`.
- The API endpoints interact with this LangGraph instance to load, save, and retrieve conversations.

This setup separates the UI from the business logic, making the application modular and easy to maintain.
