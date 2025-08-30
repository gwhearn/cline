# Changelog

All notable changes to the Ansible Playbook Generator project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial CHANGELOG.md file to track project changes
- LLM abstraction layer to support multiple LLM providers (OpenAI and Ollama)
- Support for Ollama as a local LLM provider
- Enhanced health check endpoint to show available LLM providers
- Provider information display in the UI

### Changed
- Refactored OpenAI service to use the new LLM abstraction layer
- Updated API routes to use dependency injection for services
- Modified configuration to support multiple LLM providers
- Updated environment variables to include Ollama settings
- Improved error handling for LLM provider failures

### Coming Soon
- Local user authentication system
- Playbook history and management
- Advanced playbook customization options
- Improved error handling and validation feedback
- Performance optimizations for local deployment
- Enhanced UI/UX including dark mode
- Template library for common playbook patterns
- Local variable management

## [0.1.0] - 2025-08-29
### Added
- Initial release
- Convert natural language descriptions into Ansible playbooks using OpenAI API
- Validate generated playbooks using ansible-lint
- Download validated playbooks with proper directory structure
- Basic web interface with Bootstrap and HTMX
