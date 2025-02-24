# Medical Q&A System

A medical question-answering system that combines local medical documents with web-based information to provide accurate, referenced medical information.

## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/Krishi03/Medical-Q-A-model.git
cd Medical-Q-A-model
pip install -r requirements.txt
```
2.Create a .env file in the root directory with:
```GOOGLE_API_KEY=your_google_api_key_here```

3.Run the application:
```
cd backend/src
python api.py
streamlit run streamlit_app.py
```

