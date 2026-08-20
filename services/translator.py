from deep_translator import GoogleTranslator, MyMemoryTranslator


def _chunk_text(text: str, max_chars: int = 400) -> list[str]:
    """
    Splits long text into smaller chunks based on line breaks and spaces
    to prevent API payload limits (e.g., MyMemory's 500-char limit) and Render IP blocks.
    """
    if len(text) <= max_chars:
        return [text]

    lines = text.splitlines(keepends=True)
    chunks = []
    current = ""

    for line in lines:
        if len(current) + len(line) <= max_chars:
            current += line
        else:
            if current:
                chunks.append(current)
                current = ""
            if len(line) > max_chars:
                words = line.split(" ")
                for word in words:
                    if len(current) + len(word) + 1 <= max_chars:
                        current += (" " if current else "") + word
                    else:
                        if current:
                            chunks.append(current)
                        current = word
            else:
                current = line
    if current:
        chunks.append(current)

    return chunks if chunks else [text]


def _translate_chunks(chunks: list[str], engine_type: str, src: str, target: str) -> str:
    translated_parts = []
    for chunk in chunks:
        if not chunk.strip():
            translated_parts.append(chunk)
            continue

        if engine_type == "google":
            result = GoogleTranslator(source=src, target=target).translate(chunk)
        elif engine_type == "mymemory":
            fallback_src = "en" if src == "auto" else src
            result = MyMemoryTranslator(source=fallback_src, target=target).translate(chunk)
        else:
            raise ValueError("Unknown translation engine")

        if not result:
            raise ValueError(f"Empty output from {engine_type}")
        translated_parts.append(result)

    return "".join(translated_parts)


def translate_text(text: str, source_lang: str, target_lang: str) -> dict:
    """
    Translates text with automatic engine failover and smart payload chunking.
    Primary Engine: GoogleTranslator
    Failover Engine: MyMemoryTranslator
    """
    clean_text = text.strip()
    src = "auto" if source_lang.strip().lower() in ["auto", "auto-detect"] else source_lang.strip()
    target = target_lang.strip()

    # Short-circuit if source and target languages are identical
    if src.lower() == target.lower():
        return {
            "translated_text": clean_text,
            "engine_used": "Direct Pass-through"
        }

    # Break text into chunks under 400 characters
    chunks = _chunk_text(clean_text, max_chars=400)

    try:
        translated = _translate_chunks(chunks, "google", src, target)
        return {
            "translated_text": translated,
            "engine_used": "Google Translate"
        }
    except Exception as primary_error:
        try:
            translated = _translate_chunks(chunks, "mymemory", src, target)
            return {
                "translated_text": translated,
                "engine_used": "MyMemory (Failover)"
            }
        except Exception as fallback_error:
            raise RuntimeError(
                f"All translation engines failed. Primary: {primary_error} | Fallback: {fallback_error}"
            ) from fallback_error