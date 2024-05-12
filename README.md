# Foody: Dive into Culinary Stories 🍲📚

## Overview
Welcome to Foody, your digital culinary guide! Foody is a unique application that combines advanced OCR technology with a sophisticated chatbot to bring the history and stories behind your favorite dishes right to your fingertips. With Foody, every meal is not just food but a journey through history and culture.

## Features
- **Image Upload**: Easily upload images of your menu, and our OCR technology will detect the text.
- **Culinary Chatbot**: Engage with our vibrant and knowledgeable chatbot who loves to share fun facts, emoji-filled stories, and historical insights about various cuisines.
- **Interactive UI**: A user-friendly interface with functionalities embedded in a sidebar for a clutter-free experience.
- **Rich Content**: Access a vast database of culinary information, from obscure dishes to popular favorites.

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Pip for Python package installation

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/foody.git
   cd foody
   ```

2. **TODO Install required libraries** 
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   - Create a `.env` file in the root directory.
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY='your_key_here'
     ```
    - Create a `.streamlit` folder in the root directory.
    - Create a `secrets.toml` file in the `.streamlit` folder.
    - Add your OpenAI API key:
     ```
     OPENAI_API_KEY='your_key_here'
     ```

4. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

### Usage
- **Upload a Menu Image**: Drag and drop your menu image in the sidebar's uploader.
- **Interact with the Chatbot**: After uploading your menu image, ask any food-related questions in the chat. The chatbot will respond with interesting stories and facts.
