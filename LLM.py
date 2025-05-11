import os
import pandas as pd
import anthropic
import gradio as gr
import random

# Note: API key should be securely handled in a production environment
API_KEY = "your-api-key"  # Replace with your Claude API key
client = anthropic.Anthropic(api_key=API_KEY)

def load_csvs(folder_path="D:/Projects Codes/Restraunts/"):
    """
    Load all CSV files from the specified folder and return their contents as a combined string.
    """
    try:
        # Ensure the folder exists
        if not os.path.exists(folder_path):
            return f"Error: Folder {folder_path} does not exist."
        
        # Get list of CSV files
        csv_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".csv")]
        if not csv_files:
            return f"No CSV files found in {folder_path}."
        
        file_texts = []
        for file in csv_files:
            file_path = os.path.join(folder_path, file)
            try:
                df = pd.read_csv(file_path)
                # Limit to first 20 rows for brevity
                data_string = f"Data from {file}:\n{df.head(20).to_string(index=False)}"
                file_texts.append(data_string)
            except Exception as e:
                file_texts.append(f"Error reading {file}: {e}")
        
        combined_data = "\n\n".join(file_texts)
        return combined_data
    except Exception as e:
        return f"Error accessing folder {folder_path}: {e}"

def make_response_chatty(base_response, is_non_technical=False):
    """
    Add friendly, conversational phrases to the response for the Forecasting Agent.
    """
    greetings = [
        "Hey, what's up?!", 
        "Yo, good to hear from you!", 
        "Hiya! What's the vibe today?", 
        "Hey there!"
    ]
    opening_alternatives = [
        "Diving right in!", 
        "Let’s get to it!", 
        "Here’s the scoop!", 
        "Ready to roll!"
    ]
    casual_phrases = [
        "Just vibing and ready to assist!", 
        "Loving the chance to dive into this!", 
        "Always fun to crunch some numbers!", 
        "So, what’s the next big thing?", 
        "Can’t wait to help you out more!"
    ]
    closing_phrases = [
        "What’s next on your radar?", 
        "Got more questions? I’m game!", 
        "Let me know what’s up next!", 
        "So, where do we go from here?", 
        "Any more insights you need?"
    ]
    
    if is_non_technical:
        # For non-technical queries, use simple, casual responses
        non_tech_responses = [
            "Yo, just chilling! What's good with you?",
            "Hey, nice to see you! What's the mood today?",
            "Hiya! Just hanging out, ready to chat! What's up?",
            "Sup? Loving the vibes! What's on your mind?"
        ]
        base_response = random.choice(non_tech_responses)
        return f"{random.choice(greetings)} {base_response} {random.choice(casual_phrases)} {random.choice(closing_phrases)}"
    
    # For technical queries (non-insights), randomly decide whether to use a greeting (50% chance)
    if random.random() < 0.5:
        opener = random.choice(greetings)
    else:
        opener = random.choice(opening_alternatives)
    
    chatty_response = f"{opener} {base_response} {random.choice(casual_phrases)} {random.choice(closing_phrases)}"
    return chatty_response

def ask_forecasting_agent(user_query, combined_data):
    """
    Handle general restaurant forecasting queries using Claude.
    """
    try:
        # Check if the query is asking for insights
        insight_keywords = ["insights", "analyze", "trends", "analysis", "overview", "performance"]
        is_insights = any(keyword in user_query.lower() for keyword in insight_keywords)
        
        # Construct prompt for forecasting
        prompt = f"You are a restaurant forecasting assistant. Use the following data to answer the query, but do not mention the names or details of the data files unless explicitly asked:\n{combined_data}\n\nUser query: {user_query}"

        # Call Anthropic API
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Handle response content
        base_response = ""
        if response.content:
            for block in response.content:
                if block.type == "text":
                    base_response += block.text + "\n"
        else:
            base_response = "No response content received from Claude."

        # Return raw response for insights, chatty for others
        if is_insights:
            return base_response.strip()
        return make_response_chatty(base_response.strip(), is_non_technical=False)

    except Exception as e:
        return f"Error querying Forecasting Agent: {e}"

def ask_scheduling_agent(user_query, combined_data):
    """
    Handle scheduling-related queries using Claude, focusing on rota data.
    """
    try:
        # Construct prompt for scheduling
        prompt = f"You are a restaurant scheduling assistant. Your task is to analyze or generate employee schedules (rotas) based on the provided data, focusing on shift assignments, employee availability, and labor costs. Use the following data, prioritizing rota-related information, but do not mention the names or details of the data files unless explicitly asked:\n{combined_data}\n\nUser query: {user_query}\n\nProvide a clear, professional response with structured shift schedules or analysis (e.g., in list or table format) without conversational phrases."

        # Call Anthropic API
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Handle response content
        base_response = ""
        if response.content:
            for block in response.content:
                if block.type == "text":
                    base_response += block.text + "\n"
        else:
            base_response = "No response content received from Claude."

        return base_response.strip()

    except Exception as e:
        return f"Error querying Scheduling Agent: {e}"

def ask_claude(user_query):
    """
    Route queries to the appropriate agent (Forecasting or Scheduling) or respond conversationally for non-technical queries.
    """
    try:
        # Check if the query is a casual greeting or non-technical
        casual_queries = [
            "hi", "hello", "hey", "what's up", "yo", "howdy", 
            "good morning", "good evening", "hiya", "sup"
        ]
        is_non_technical = user_query.strip().lower() in casual_queries
        
        if is_non_technical:
            # Return a chatty, non-technical response without accessing data
            return make_response_chatty("", is_non_technical=True)
        
        # Check if the query is scheduling-related
        scheduling_keywords = ["schedule", "rota", "shift", "staffing", "employee schedule"]
        is_scheduling = any(keyword in user_query.lower() for keyword in scheduling_keywords)
        
        # Load data from local CSV files
        combined_data = load_csvs()
        if combined_data.startswith("Error"):
            return combined_data

        # Route to appropriate agent
        if is_scheduling:
            return ask_scheduling_agent(user_query, combined_data)
        return ask_forecasting_agent(user_query, combined_data)

    except Exception as e:
        return f"Error processing query: {e}"

# Define Gradio interface
interface = gr.Interface(
    fn=ask_claude,
    inputs=gr.Textbox(label="Your Question", placeholder="Ask about restaurant forecasting, schedules, or just say hi!"),
    outputs="text",
    title="Multi-Agent Restaurant Assistant",
    description="Ask about restaurant forecasting, employee schedules, or just say hi for a friendly chat! Data is sourced from local CSV files in D:/Projects Codes/Restraunts/."
)

if __name__ == "__main__":
    interface.launch()