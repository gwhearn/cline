# Ansible Playbook Generator

A web application that generates Ansible playbooks from natural language descriptions using AI.

## Features

- Convert natural language descriptions into Ansible playbooks
- Validate generated playbooks using ansible-lint
- Download validated playbooks with proper directory structure
- Secure Python-based implementation

## Technology Stack

- Backend: FastAPI (Python)
- Frontend: Jinja2 templates with Bootstrap and HTMX
- AI: OpenAI API
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

4. Create a `.env` file based on `.env.example` and add your OpenAI API key:
   ```
   cp .env.example .env
   # Edit .env and add your OpenAI API key
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

- User authentication and authorization
- Host and owner validation
- Playbook history and management
- Advanced playbook customization options
- Integration with Ansible Tower/AWX

## License

MIT
