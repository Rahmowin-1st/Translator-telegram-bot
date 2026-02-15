
# =========================================
# TELEGRAM AI TRANSLATOR BOT - MONOLITH
# =========================================

import os
import logging
import sqlite3
import asyncio
import datetime
import base64
import json
import threading
from io import BytesIO

import requests
from flask import Flask, request, redirect

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from gtts import gTTS
from google import genai
from google.genai import types

# =========================================
# LOGGING
# =========================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# =========================================
# CONFIG
# =========================================

BOT_TOKEN = os.getenv("BOT_TOKEN") or "7591558748:AAH-idabaw_3JlEYpdA4QhPhpOoLVOqAVnk"
AI_INTEGRATIONS_GEMINI_API_KEY = os.environ.get("AI_INTEGRATIONS_GEMINI_API_KEY")
AI_INTEGRATIONS_GEMINI_BASE_URL = os.environ.get("AI_INTEGRATIONS_GEMINI_BASE_URL")

client = genai.Client(
    api_key=AI_INTEGRATIONS_GEMINI_API_KEY,
