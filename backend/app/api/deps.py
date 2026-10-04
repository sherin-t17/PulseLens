"""
No login system: each browser creates a random ID and sends it in the
X-Client-Id header, so people only see their own measurements.
"""

import re

from fastapi import Header


def get_client_id(x_client_id: str = Header(default="anonymous")):
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "", x_client_id)[:64]
    return cleaned or "anonymous"