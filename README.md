# AI Service

This is a middleware AI service that provides a layer of abstraction between your application and a large language model (LLM). Currently, it uses Gemini, but it can be easily adapted to use other models in the future.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.11+
- An API key for the Gemini API

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/jakubzajkowski/cowrite-ai-service.git
    ```
2.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Create a `.env` file in the root directory and add your Gemini API key:
    ```
    GEMINI_API_KEY="YOUR_API_KEY"
    ```
4.  Run the application:
    ```bash
    uvicorn app.main:app --reload
    ```
All development command instructions in `Makefile`