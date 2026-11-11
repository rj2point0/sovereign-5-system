#!/usr/bin/env python3
"""
MCP VIDEO GENERATION SERVER — GOOGLE VEO 3.1 (`mcp-video-generation-veo2` / `veo-3.1-generate-preview`)
=======================================================================================================
Official Google GenAI SDK (`google-genai`) + Google Flow (`flow.google.com` / `labs.google/fx/tools/flow`)
wrapper supporting:
  - `veo-3.1-generate-preview` & `veo-3.1-fast-generate-preview`
  - `generate_audio=True` (native dialogue & lip-sync audio)
  - `aspect_ratio="9:16"`
  - `reference_images` (`VideoGenerationReferenceImage` / `ASSET`) for 100% character consistency

V2 VIRAL STORYTELLING & RETENTION SPEC (LOCKED FOR BATCH 18+ / SHORT_060+ — FROZEN THROUGH SHORT_059):
  1. Frame-0 Visual Prop Hook (0.0s–1.8s): Flash crisp high-contrast iMessage thread prop (3 blue bubbles ->
     cold "k" or "Read 11:42 PM") on Frame 0 beside Maya to prime the $2.99 text-script unlock.
  2. Zero Spoken Bio Pitch: NEVER speak "link in bio", "tap our bio", or "check your score" out loud;
     the silent Lower-Third Blurred iMessage + 96% SOULMATE LOCK card handles 100% of CTA work in the final 3s.
  3. "Last Dab" Seamless Replay Loop: Write Julian's final spoken syllable first so it grammatically/emotionally
     loops straight into Maya's opening word on auto-replay (targeting APV > 110%).
  4. Jagged Rhythm + But/Therefore Conflict Chain: Ban uniform 15-word AI lines; enforce 2-word punch ->
     medium setup -> longer `but` / `therefore` twist in intimate midnight voice-note cadence.
"""

import os
import sys
import time
import json
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional, Tuple

from google import genai
from google.genai import types


def load_dotenv_vars(env_path: str = r"c:\Users\User\5numsystem\.env") -> Dict[str, str]:
    out: Dict[str, str] = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    out[k.strip()] = v.strip()
                    os.environ.setdefault(k.strip(), v.strip())
    return out


class Veo31VideoGenerator:
    """
    Unified Google Veo 3.1 generator supporting:
    1. Official `google-genai` SDK (`veo-3.1-generate-preview` / `veo-3.1-fast-generate-preview`)
    2. Vertex AI Express Mode (`aiplatform.googleapis.com` with `AQ.` API key & project `828136803921`)
    3. Authenticated Google Flow Ultra (`https://flow.google.com` / `https://labs.google/fx/tools/flow`) on CDP port 9224
    """

    def __init__(self):
        load_dotenv_vars()
        self.api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY") or ""
        self.project = os.environ.get("GOOGLE_CLOUD_PROJECT", "828136803921")
        self.location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

    def verify_vertex_veo_ready(self) -> Tuple[bool, str]:
        if not self.api_key:
            return False, "No GOOGLE_API_KEY set"
        url = (
            f"https://aiplatform.googleapis.com/v1beta1/projects/{self.project}"
            f"/locations/{self.location}/publishers/google/models/veo-3.1-generate-preview:predictLongRunning?key={self.api_key}"
        )
        req = urllib.request.Request(
            url,
            data=json.dumps({"instances": []}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                return True, f"HTTP {resp.status}"
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            # If 400 INVALID_ARGUMENT (empty instances) instead of 403/401, the API is enabled and authenticated!
            if e.code == 400 and "PERMISSION_DENIED" not in body and "SERVICE_DISABLED" not in body:
                return True, "Vertex AI API enabled and authenticated (HTTP 400 on empty probe)"
            return False, f"HTTP {e.code}: {body[:240]}"
        except Exception as e:
            return False, str(e)

    def generate_video_sdk(
        self,
        prompt: str,
        output_mp4: str,
        reference_image_path: Optional[str] = None,
        model: str = "veo-3.1-generate-preview",
        aspect_ratio: str = "9:16",
        generate_audio: bool = True,
        duration_seconds: int = 8,
    ) -> str:
        """
        Calls `client.models.generate_videos` with `veo-3.1-generate-preview`,
        `generate_audio=True`, `aspect_ratio="9:16"`, and `reference_images`.
        """
        is_aq = self.api_key.startswith("AQ.")
        client = (
            genai.Client(vertexai=True, api_key=self.api_key)
            if is_aq
            else genai.Client(api_key=self.api_key)
        )

        cfg_kwargs: Dict[str, Any] = {
            "aspect_ratio": aspect_ratio,
            "number_of_videos": 1,
        }
        if generate_audio:
            cfg_kwargs["generate_audio"] = True
        if duration_seconds:
            cfg_kwargs["duration_seconds"] = duration_seconds

        ref_img = None
        if reference_image_path and os.path.exists(reference_image_path):
            pil_im = types.Image.from_file(location=reference_image_path)
            cfg_kwargs["reference_images"] = [
                types.VideoGenerationReferenceImage(
                    image=pil_im,
                    reference_type="ASSET",
                )
            ]

        config = types.GenerateVideosConfig(**cfg_kwargs)
        operation = client.models.generate_videos(
            model=model,
            source=types.GenerateVideosSource(prompt=prompt),
            config=config,
        )
        while not operation.done:
            time.sleep(5)
            operation = client.operations.get(operation)

        vid = operation.result.generated_videos[0].video
        if getattr(vid, "video_bytes", None):
            with open(output_mp4, "wb") as f:
                f.write(vid.video_bytes)
        elif getattr(vid, "uri", None):
            urllib.request.urlretrieve(vid.uri, output_mp4)
        return output_mp4
