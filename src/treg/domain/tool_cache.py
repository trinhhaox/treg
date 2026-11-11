"""TTL Response Cache for tools with strict resource bounds (max 1MB per body, automatic cleanup)."""
from __future__ import annotations

from datetime import timedelta
import hashlib
import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import delete, select

from ..models import ToolCacheRecord
from ..timeutil import utcnow_naive

from urllib.parse import parse_qsl, urlencode

log = logging.getLogger(__name__)

# Max response size to cache: 1MB. Larger responses stream directly without consuming memory/disk.
MAX_CACHE_BODY_BYTES = 1_048_576

# Max entries per tool to prevent unbounded growth
MAX_ENTRIES_PER_TOOL = 1_000


def make_cache_key(tool_id: int, method: str, path: str, query: str, body: bytes) -> str:
    """Deterministic SHA-256 cache key from request parameters."""
    if query:
        pairs = sorted(parse_qsl(query, keep_blank_values=True))
        norm_query = urlencode(pairs)
    else:
        norm_query = ""
    body_hash = hashlib.sha256(body).hexdigest() if body else "empty"
    raw = f"{tool_id}:{method.upper()}:{path}:{norm_query}:{body_hash}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


async def lookup_cache(
    db: AsyncSession,
    tool_id: int,
    cache_key: str,
) -> ToolCacheRecord | None:
    """Find a fresh, non-expired cache record for this tool and key."""
    now = utcnow_naive()
    stmt = (
        select(ToolCacheRecord)
        .where(
            ToolCacheRecord.tool_id == tool_id,
            ToolCacheRecord.cache_key == cache_key,
            ToolCacheRecord.expires_at > now,
        )
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def store_cache(
    db: AsyncSession,
    *,
    tool_id: int,
    org_id: int,
    cache_key: str,
    method: str,
    path: str,
    status_code: int,
    headers: dict[str, str],
    body: bytes,
    ttl_seconds: int,
) -> bool:
    """Store a response in cache if eligible (2xx status, under 1MB, positive TTL)."""
    if ttl_seconds <= 0:
        return False
    if not (200 <= status_code < 300):
        return False
    if len(body) > MAX_CACHE_BODY_BYTES:
        return False

    now = utcnow_naive()
    expires_at = now + timedelta(seconds=ttl_seconds)

    # Safe headers only
    safe_headers = {
        k: v for k, v in headers.items()
        if k.lower() in ("content-type", "x-treg-cache", "etag", "content-language")
    }

    try:
        # Check existing to update
        existing = (await db.execute(
            select(ToolCacheRecord).where(
                ToolCacheRecord.tool_id == tool_id,
                ToolCacheRecord.cache_key == cache_key,
            )
        )).scalar_one_or_none()

        if existing is not None:
            existing.status_code = status_code
            existing.headers_json = json.dumps(safe_headers)
            existing.response_body = body
            existing.body_size = len(body)
            existing.expires_at = expires_at
        else:
            rec = ToolCacheRecord(
                tool_id=tool_id,
                org_id=org_id,
                cache_key=cache_key,
                method=method.upper(),
                path_url=path[:1024],
                status_code=status_code,
                headers_json=json.dumps(safe_headers),
                response_body=body,
                body_size=len(body),
                created_at=now,
                expires_at=expires_at,
            )
            db.add(rec)

        await db.commit()
        return True
    except Exception as exc:  # noqa: BLE001
        log.warning("Failed to store tool cache: %s", exc)
        await db.rollback()
        return False


async def gc_expired_cache(db: AsyncSession) -> int:
    """Opportunistic cleanup of expired cache entries."""
    now = utcnow_naive()
    try:
        stmt = delete(ToolCacheRecord).where(ToolCacheRecord.expires_at <= now)
        res = await db.execute(stmt)
        await db.commit()
        return res.rowcount or 0
    except Exception as exc:  # noqa: BLE001
        log.warning("Failed to GC expired tool cache: %s", exc)
        await db.rollback()
        return 0
