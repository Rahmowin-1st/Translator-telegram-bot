# Telegram AI Translator Bot (Monolith Version)

A full-featured Telegram bot built with Python that provides AI-powered translation, OCR, voice transcription, and user management in a single monolithic architecture.

## Overview

This project integrates Telegram Bot API with Google Gemini AI to deliver real-time translation, text extraction from images, and voice transcription directly inside Telegram chats.

The bot includes user tracking, translation history storage, admin tools, and multi-language system interface support.

## Core Features

### 🌍 AI Translation
- Automatic language detection (ISO 639-1)
- Text-to-text translation via Gemini API
- Target language selection
- Force-translate option when detected language equals target

### 🖼 Image OCR + Translation
- Extracts text from images using Gemini Vision
- Automatically translates extracted content
- Option to view original extracted text

### 🎙 Voice Processing
- Transcribes OGG voice messages using Gemini
- Automatically translates transcribed content
- Generates translated voice response using gTTS

### 📚 Extra Language Tools
- Short meaning explanation (1 sentence)
- Synonym generation (3 words)
- Re-translation to another selected language
- Access to original detected text

### 👤 User System
- SQLite-based user storage
- System language selection (UZ / EN / RU)
- Saved target language
- Translation history per user
- Premium flag support
- Block flag structure (extensible)

### 👨‍💼 Admin Panel
- User statistics (total users, messages, 24h activity)
- Language usage breakdown
- Broadcast messaging
- Full user list with join date
- Access to individual user history
- Database export command

## Technical Stack

- Python 3.12
- python-telegram-bot (async version)
- Google Gemini API (text + vision + audio)
- SQLite
- Flask (health-check endpoint)
- gTTS (text-to-speech)
- Asyncio architecture

## Architecture

This project follows a monolithic structure:

- Single main execution file
- Modular function separation (DB, AI engine, handlers)
- Async request handling
- Bot polling system
- Embedded Flask server for uptime monitoring

## Database Structure

### Users Table
- user_id
- username
- full_name
- phone
- joined_date
- system_lang
- last_target_lang
- premium
- blocked

### History Table
- user_id
- role (user / assistant)
- content
- detected_lang
- target_lang
- timestamp

## Workflow

1. User sends text / image / voice.
2. Language is detected using Gemini.
3. Content is processed (translate / OCR / transcribe).
4. Result is saved in database.
5. Response is returned with interactive inline options.
6. Optional TTS audio is generated.

## Deployment

- Polling-based bot
- Local SQLite storage
- Flask health endpoint for uptime services

## Status

Production-ready structure.
Scalable with modular refactor (microservice separation possible in future).