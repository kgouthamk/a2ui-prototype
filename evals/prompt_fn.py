"""Promptfoo prompt function — uses the REAL agent prompt so evals never drift
from production. Returns chat messages as JSON.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.agent.prompt import build_messages  # noqa: E402


def make_prompt(context):
    markdown = context["vars"]["markdown"]
    return json.dumps(build_messages(markdown))
