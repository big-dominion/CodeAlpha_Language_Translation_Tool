from functools import lru_cache
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from services.audio import _get_supported_langs, generate_tts_audio
from services.translator import translate_text

app = FastAPI(
    title="DOMINION OmniTranslate API",
    description="Enterprise-Grade Neural Translation Gateway with Automated Failover & TTS Streaming",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TranslationRequest(BaseModel):
    text: str = Field(..., max_length=5000, description="Text string to translate")
    source_lang: str = Field(default="auto", description="Source language code")
    target_lang: str = Field(
        ..., min_length=2, max_length=10, description="Target language code"
    )

    @field_validator("text", "source_lang", "target_lang", mode="before")
    @classmethod
    def sanitize_inputs(cls, v: str) -> str:
        return v.strip() if isinstance(v, str) else v


class TTSRequest(BaseModel):
    text: str = Field(
        ..., max_length=5000, description="Text string for speech synthesis"
    )
    lang: str = Field(
        ...,
        min_length=2,
        max_length=10,
        description="Language code for speech synthesis",
    )
    accent: str = Field(
        default="us",
        description="Regional accent tld for gTTS (e.g., us, co.uk, com.ng, co.in)",
    )

    @field_validator("text", "lang", "accent", mode="before")
    @classmethod
    def sanitize_inputs(cls, v: str) -> str:
        return v.strip() if isinstance(v, str) else v


@lru_cache(maxsize=512)
def cached_translation(text: str, source_lang: str, target_lang: str) -> dict:
    return translate_text(text, source_lang, target_lang)


@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "service": "DOMINION OmniTranslate API"}


@app.post("/api/v1/translate")
async def handle_translation(req: TranslationRequest):
    if not req.text:
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")
    try:
        result = cached_translation(req.text, req.source_lang, req.target_lang)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/tts")
async def handle_tts(req: TTSRequest):
    if not req.text:
        raise HTTPException(status_code=400, detail="Text required for audio generation.")
    try:
        audio_b64 = generate_tts_audio(req.text, req.lang, req.accent.lower())
        return {"status": "success", "audio_base64": audio_b64}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/tts/supported-langs")
async def get_supported_tts_langs():
    return {"status": "success", "langs": sorted(_get_supported_langs().keys())}


# Mount static frontend assets last so API routes take precedence
app.mount("/", StaticFiles(directory="static", html=True), name="static")