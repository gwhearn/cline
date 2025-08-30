# Ansible Playbook Generator

A web application that generates Ansible playbooks from natural language descriptions using AI, with support for both cloud-based and local LLM providers.

## Features

- Convert natural language descriptions into Ansible playbooks
- Support for multiple LLM providers (OpenAI and Ollama)
- Run completely locally with Ollama or use OpenAI's API
- Validate generated playbooks using ansible-lint
- Download validated playbooks with proper directory structure
- Secure Python-based implementation

## Technology Stack

- Backend: FastAPI (Python)
- Frontend: Jinja2 templates with Bootstrap and HTMX
- AI: OpenAI API or Ollama (local LLM)
- Validation: ansible-lint

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ansible-playbook-generator.git
   cd ansible-playbook-generator
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example` and configure your LLM provider:
   ```
   cp .env.example .env
   # Edit .env and configure your preferred LLM provider
   ```

   You can choose between OpenAI (cloud-based) or Ollama (local):
   
   For OpenAI:
   ```
   PREFERRED_LLM_PROVIDER=openai
   OPENAI_API_KEY=your_openai_api_key_here
   ```
   
   For Ollama (local LLM):
   ```
   PREFERRED_LLM_PROVIDER=ollama
   OLLAMA_API_BASE=http://localhost:11434
   OLLAMA_MODEL=llama3
   ```
   
   Note: To use Ollama, you need to [install Ollama](https://ollama.ai/download) and pull your preferred model:
   ```
   ollama pull llama3
   ```

## Usage

1. Start the application:
   ```
   uvicorn app.main:app --reload
   ```

2. Open your browser and navigate to `http://localhost:8000`

3. Enter a natural language description of the Ansible task you want to perform

4. Review the generated playbook and validation results

5. Download the validated playbook

## Development

- API documentation is available at `/docs` or `/redoc`
- Run tests with `pytest`

## Future Enhancements

- Local user authentication and authorization
- Playbook history and management
- Advanced playbook customization options
- Improved error handling and validation feedback
- Performance optimizations for local deployment
- Enhanced UI/UX including dark mode
- Template library for common playbook patterns
- Local variable management
- Integration with Ansible Tower/AWX

## License

MIT
