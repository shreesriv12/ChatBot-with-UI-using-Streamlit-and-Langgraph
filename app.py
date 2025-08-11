from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import sqlite3
import os
import uuid
import json

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure random key
CORS(app)

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest", 
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

# Database connection
conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

# Build graph
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    return list(all_threads)

def generate_thread_id():
    return str(uuid.uuid4())

def load_conversation(thread_id):
    try:
        state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
        if state.values and 'messages' in state.values:
            messages = []
            for msg in state.values['messages']:
                if isinstance(msg, HumanMessage):
                    messages.append({'role': 'user', 'content': msg.content})
                else:
                    messages.append({'role': 'assistant', 'content': msg.content})
            return messages
        return []
    except:
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/threads', methods=['GET'])
def get_threads():
    threads = retrieve_all_threads()
    return jsonify({'threads': threads})

@app.route('/api/thread/new', methods=['POST'])
def create_new_thread():
    thread_id = generate_thread_id()
    session['current_thread'] = thread_id
    return jsonify({'thread_id': thread_id})

@app.route('/api/thread/<thread_id>/messages', methods=['GET'])
def get_thread_messages(thread_id):
    messages = load_conversation(thread_id)
    return jsonify({'messages': messages})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    thread_id = data.get('thread_id')
    
    if not thread_id:
        thread_id = session.get('current_thread')
        if not thread_id:
            thread_id = generate_thread_id()
            session['current_thread'] = thread_id
    
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
    
    try:
        config = {'configurable': {'thread_id': thread_id}}
        
        # Stream the response
        response_content = ""
        for message_chunk, metadata in chatbot.stream(
            {'messages': [HumanMessage(content=user_message)]},
            config=config,
            stream_mode='messages'
        ):
            if message_chunk.content:
                response_content += message_chunk.content
        
        return jsonify({
            'response': response_content,
            'thread_id': thread_id
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    """Alternative streaming endpoint using Server-Sent Events"""
    data = request.json
    user_message = data.get('message', '')
    thread_id = data.get('thread_id')
    
    if not thread_id:
        thread_id = session.get('current_thread')
        if not thread_id:
            thread_id = generate_thread_id()
            session['current_thread'] = thread_id
    
    def generate():
        try:
            config = {'configurable': {'thread_id': thread_id}}
            
            for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_message)]},
                config=config,
                stream_mode='messages'
            ):
                if message_chunk.content:
                    yield f"data: {json.dumps({'chunk': message_chunk.content})}\n\n"
            
            yield f"data: {json.dumps({'done': True, 'thread_id': thread_id})}\n\n"
        
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return app.response_class(
        generate(),
        mimetype='text/plain',
        headers={'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache'}
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)