# Phase 2: Services

## Overview
This directory contains the source code for the microservices and frontend application.

## Services
- **Document Service** (`/document-service`): Manages PDF uploads, text extraction, and storage.
- **Chat Service** (`/chat-service`): Provides an AI conversational interface using LLMs.
- **Quiz Service** (`/quiz-service`): Generates quizzes from processed content.
- **STT Service** (`/stt-service`): Converts speech to text.
- **TTS Service** (`/tts-service`): Converts text to speech.
- **User Service** (`/user-service`): Authentication and authorization (RBAC).

## Frontend
- **Frontend Web** (`/frontend-web`): A responsive web interface built with HTML, CSS, and JavaScript.

## Running Locally
Configuration is handled via `docker-compose.yml` (in the parent directory).
```bash
docker-compose up --build
```
