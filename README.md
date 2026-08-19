# DOMINION OmniTranslate : CodeAlpha AI Edition

DOMINION OmniTranslate is a lightweight, production-ready neural translation gateway. It provides text translation across 130+ languages, browser-based voice recognition for dictation, and text-to-speech playback with selectable regional accents, all served from a single FastAPI backend with zero Node.js build overhead.

This project was built as part of the CodeAlpha AI Engineering program.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture Notes](#architecture-notes)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation and Setup](#installation-and-setup)
- [Running the Application](#running-the-application)
- [API Reference](#api-reference)
- [Accent Support Notes](#accent-support-notes)
- [Known Limitations](#known-limitations)
- [Deployment](#deployment)
- [Acknowledgements](#acknowledgements)

## Overview

DOMINION OmniTranslate pairs a single-file React frontend (loaded via CDN, no build step) with a FastAPI backend that exposes a small set of REST endpoints for translation and speech synthesis. The backend uses an automatic failover strategy: if the primary translation engine fails, a secondary engine takes over so the user rarely sees a hard error.

## Key Features

- Broad Language Support: translate text across 130+ languages using Google Translate as the primary engine.
- Automatic Engine Failover: if the primary translation engine (Google Translate) fails or is rate limited, the app automatically retries using MyMemory Translator so translation stays available.
- Browser Voice Recognition: dictate source text directly using the Web Speech API, with automatic session resumption if the browser times out mid-recording.
- Text-to-Speech Synthesis: converts translated output into playable audio using gTTS.
- Regional Accent Selection: for English output specifically, users can choose between US, UK, Australian, Indian, Nigerian, and Canadian accents.
- Response Caching: translation results are cached in-memory (LRU cache) to avoid repeat calls for identical text and language pairs.
- Zero-Build Frontend: the entire UI lives in one static index.html file; there is no npm install or build pipeline required.
- Responsive Dark Mode UI: built with Tailwind CSS and Lucide icons, including an animated particle background on the welcome screen.

## Architecture Notes

The frontend is a monolithic single-file React application that uses in-browser Babel for JSX transpilation, loaded entirely through CDN scripts (React, ReactDOM, Babel Standalone, Tailwind, Lucide). This design choice was intentional:

- Zero-Node Deployment: removes the need for a Node.js or npm build environment on the production server, keeping the deployed container lightweight.
- Single Process Serving: FastAPI serves both the JSON API (under /api/v1/) and the static frontend from the same process and port.
- Micro-SaaS Efficiency: delivers a full React interface with Tailwind styling and Web Speech API access without any build tooling overhead, ideal for small deployments on platforms like Render.

## Tech Stack

### Backend

- Python 3.10+
- FastAPI: the web framework powering the JSON API
- Uvicorn: ASGI server used to run the FastAPI app
- deep-translator: wraps GoogleTranslator (primary) and MyMemoryTranslator (failover) for text translation
- gTTS: Google Text-to-Speech library used for audio synthesis
- Pydantic: request and response data validation
- uv: fast Python package and virtual environment manager used for local development

### Frontend

- React 18 (loaded via CDN, no bundler)
- Tailwind CSS (loaded via CDN)
- Babel Standalone (in-browser JSX transpilation)
- Lucide Icons (loaded via CDN)
- Web Speech API (native browser speech recognition, no external dependency)

## Project Structure

```
CodeAlpha_Language_Translation_Tool/
|-- services/
|   |-- __init__.py         Package marker for the services module
|   |-- audio.py            TTS generation and accent (tld) routing logic
|   |-- translator.py       Core translation logic with engine failover
|-- static/
|   |-- index.html          Monolithic React frontend application
|   |-- logo.avif           Application logo (optimized format)
|   |-- logo.jpg            Application logo (fallback format) 
|-- .gitignore               Files and folders excluded from version control
|-- .python-version          Pinned Python version for uv
|-- main.py                  FastAPI application entry point and route definitions
|-- pyproject.toml           Project metadata and dependency declaration for uv
|-- README.md                Project documentation (this file)
|-- requirements.txt         Pinned dependency list for pip based installs
|-- uv.lock                  Locked, reproducible dependency versions for uv
```

## Prerequisites

- Python 3.10 or newer installed and available on your PATH
- Git installed for cloning the repository
- uv installed (recommended) or pip as a fallback package installer
- A modern browser (Chrome or Edge recommended) for full Web Speech API support during voice dictation

## Installation and Setup

These steps assume you are using uv, which is how this project was originally set up and is the recommended workflow.

1. Clone the repository

```
git clone https://github.com/big-dominion/CodeAlpha_Language_Translation_Tool.git
cd CodeAlpha_Language_Translation_Tool
```

2. Create the virtual environment

```
uv venv
```

3. Activate the virtual environment

Windows:
```
.venv\Scripts\activate
```

macOS or Linux:
```
source .venv/bin/activate
```

4. Install dependencies

With the virtual environment active, install everything listed in requirements.txt:

```
uv pip install -r requirements.txt
```

If you prefer plain pip instead of uv, the equivalent command is:

```
pip install -r requirements.txt
```

## Running the Application

Start the Uvicorn server, which will host the API and serve the static frontend from the same process:

```
uvicorn main:app --reload
```

Once the server starts, open your browser and navigate to:

```
http://localhost:8000
```

The --reload flag is intended for local development only; omit it in production.

## API Reference

All endpoints are prefixed with /api/v1.

### GET /api/v1/health

Monitors server status and confirms service availability.

Successful Response:

{  
  "status": "healthy",  
  "service": "DOMINION OmniTranslate API"  
}

### POST /api/v1/translate

Translates text from a source language to a target language, with automatic failover between engines.

Request body:

{

  "text": "Good morning",

  "source\_lang": "auto",

  "target\_lang": "es"

}

Successful response:

{

  "status": "success",

  "data": {

    "translated\_text": "Buenos dias",

    "engine\_used": "Google Translate"

  }

}

Notes:

- source\_lang accepts "auto" or "auto-detect" for automatic language detection.  
- text is limited to 5000 characters.  
- If the primary engine (Google Translate) fails, the response will report "engine\_used": "MyMemory (Failover)" instead, and the request will still succeed as long as the failover engine is reachable.

### POST /api/v1/tts

Converts text into speech and returns base64 encoded MP3 audio.

Request body:

{

  "text": "Buenos dias",

  "lang": "es",

  "accent": "us"

}

Successful response:

{

  "status": "success",

  "audio\_base64": "\<base64 encoded mp3 data\>"

}

Notes:

- text is limited to 1000 characters.  
- accent is optional and only meaningfully affects output when lang is "en"; for all other languages it is ignored by the synthesis engine.  
- If the requested lang is not supported by the TTS engine, the API returns a 400 error with an explanatory message instead of a 500 error.

### GET /api/v1/tts/supported-langs

Returns the list of language codes currently supported for text-to-speech playback.

Successful response:

{

  "status": "success",

  "langs": \["ar", "de", "en", "es", "fr", "..."\]

}

## Accent Support Notes

The accent selector only appears in the UI when the target language is English, since gTTS only exposes distinct regional voices for English through the tld parameter. The documented and currently used accent codes are:

- US: us  
- UK: co.uk  
- Australia: com.au  
- India: co.in  
- Nigeria: com.ng  
- Canada: ca

## Known Limitations

- Google's text-to-speech backend has consolidated many of its regional voices over time. Some accents (particularly Canada and Ireland style codes) may sound very close to the US default even though the correct tld is being sent; this is a known upstream limitation of gTTS and not a bug in this codebase.  
- Both translation engines (Google Translate and MyMemory) are unofficial or free tier services accessed without an API key. They can be rate limited or temporarily unavailable, which is why the failover mechanism and in-memory caching exist.  
- Voice dictation quality depends entirely on the user's browser and operating system implementation of the Web Speech API; not all browsers support all languages equally.

## Deployment

This project is designed to deploy cleanly as a single web service (for example on Render):

- The Uvicorn process serves both the API routes under /api/v1 and the static frontend from the static directory in one process, on one port.  
- No separate frontend build step, static file host, or Node.js runtime is required.  
- Ensure the platform's start command matches the local run command, for example: uvicorn main:app \--host 0.0.0.0 \--port $PORT

## Acknowledgements

Developed by Samson Kayode Olawumi for the CodeAlpha AI Engineering Project.  