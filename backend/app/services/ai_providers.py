import asyncio
import base64
import json
import logging

from app.config import settings

logger = logging.getLogger(__name__)


def parse_json_response(text: str) -> dict | None:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
        logger.warning("Failed to parse JSON from AI response: %s", text[:200])
        return None


async def extract_with_gemini(prompt: str, file_data: bytes, mime: str) -> dict | None:
    try:
        from google import genai

        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-2.0-flash",
            contents=[
                genai.types.Part.from_bytes(data=file_data, mime_type=mime),
                prompt,
            ],
        )

        return parse_json_response(response.text)

    except Exception as e:
        logger.error("Gemini extraction failed: %s", e)
        return None


async def extract_with_anthropic(
    prompt: str, file_data: bytes, mime: str
) -> dict | None:
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        b64_data = base64.standard_b64encode(file_data).decode("utf-8")

        media_type_map = {
            "application/pdf": "application/pdf",
            "image/jpeg": "image/jpeg",
            "image/png": "image/png",
            "image/webp": "image/webp",
        }
        media_type = media_type_map.get(mime, "application/pdf")

        message = await asyncio.to_thread(
            client.messages.create,
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "document"
                            if media_type == "application/pdf"
                            else "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": b64_data,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )

        return parse_json_response(message.content[0].text.strip())

    except Exception as e:
        logger.error("Anthropic extraction failed: %s", e)
        return None


async def extract_with_groq(prompt: str, file_data: bytes, mime: str) -> dict | None:
    try:
        from groq import Groq

        client = Groq(api_key=settings.GROQ_API_KEY)
        b64_data = base64.standard_b64encode(file_data).decode("utf-8")

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64_data}"},
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ]

        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="llama-3.2-90b-vision-preview",
            messages=messages,
            max_tokens=2048,
        )

        return parse_json_response(response.choices[0].message.content)

    except Exception as e:
        logger.error("Groq extraction failed: %s", e)
        return None


async def call_text_ai(
    prompt: str,
    file_data: bytes | None = None,
    mime_type: str = "application/pdf",
) -> dict | None:
    providers: list[tuple[str, object]] = []
    if settings.GEMINI_API_KEY:
        providers.append(("gemini", _gemini_text_call))
    if settings.GROQ_API_KEY:
        providers.append(("groq", _groq_text_call))

    for name, fn in providers:
        try:
            result = await fn(prompt, file_data, mime_type)
            if result:
                return result
        except Exception as e:
            logger.warning("Text AI provider %s failed: %s, trying next", name, e)
            continue

    return None


async def _gemini_text_call(
    prompt: str, file_data: bytes | None, mime_type: str
) -> dict | None:
    from google import genai

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    contents = []
    if file_data:
        contents.append(
            genai.types.Part.from_bytes(data=file_data, mime_type=mime_type)
        )
    contents.append(prompt)

    response = await asyncio.to_thread(
        client.models.generate_content, model="gemini-2.0-flash", contents=contents
    )
    return parse_json_response(response.text)


async def _groq_text_call(
    prompt: str, file_data: bytes | None, mime_type: str
) -> dict | None:
    import base64 as b64mod

    from groq import Groq

    client = Groq(api_key=settings.GROQ_API_KEY)
    messages_content = []

    if file_data:
        b64 = b64mod.standard_b64encode(file_data).decode("utf-8")
        messages_content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{b64}"},
            }
        )
    messages_content.append({"type": "text", "text": prompt})

    response = await asyncio.to_thread(
        client.chat.completions.create,
        model="llama-3.2-90b-vision-preview"
        if file_data
        else "llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": messages_content}],
        max_tokens=2048,
    )
    return parse_json_response(response.choices[0].message.content)
