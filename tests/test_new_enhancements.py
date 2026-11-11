"""Tests for new platform enhancements: Export Activity CSV and 1-click Test Connection."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import pytest
from sqlmodel import select

from treg import crypto
from treg.infra.db import session_maker
from treg.models import CallRecord, Org, Secret
from test_tag_billing import _org_id


async def test_export_activity_csv(clients):
    org = await _org_id(clients)
    now = datetime(2026, 11, 12, 10, 0, 0)
    async with session_maker() as db:
        c1 = CallRecord(
            org_id=org,
            user_email="dev@example.com",
            tool_name="web_search",
            method="GET",
            path="/search?q=treg",
            status_code=200,
            duration_ms=85,
            cost_charged_micro=5000,
            api_key_name="Agent-Claude",
            cached=True,
            created_at=now,
        )
        c2 = CallRecord(
            org_id=org,
            user_email="dev@example.com",
            tool_name="image_gen",
            method="POST",
            path="/generate",
            status_code=201,
            duration_ms=420,
            cost_charged_micro=20000,
            api_key_name="Agent-Gemini",
            cached=False,
            created_at=now + timedelta(seconds=10),
        )
        db.add_all([c1, c2])
        await db.commit()

    resp = await clients.get("/activity/export.csv")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]
    text = resp.text
    # Check UTF-8 BOM
    assert text.startswith("\ufeff")
    # Check headers
    assert "Thời gian (UTC)" in text
    assert "Chi phí ($ USD)" in text
    assert "web_search" in text
    assert "image_gen" in text
    assert "Agent-Claude" in text
    assert "Có" in text  # cached
    assert "Không" in text  # not cached


async def test_single_connection_ping(clients):
    org = await _org_id(clients)
    async with session_maker() as db:
        sec = Secret(
            org_id=org,
            name="openai-test",
            provider="openai",
            kind="key",
            value=crypto.encrypt("sk-test-1234567890"),
            owner="owner@example.com",
        )
        db.add(sec)
        await db.commit()
        await db.refresh(sec)
        secret_id = sec.id

    resp = await clients.post(f"/connections/{secret_id}/test")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert "latency_ms" in data
    assert data["status"] == "ok"
    assert "message" in data

    # Verify that health status was updated in database
    async with session_maker() as db:
        updated = (await db.execute(select(Secret).where(Secret.id == secret_id))).scalar_one()
        assert updated.health_status == "ok"
        assert updated.health_checked_at is not None


async def test_tool_cache_domain(clients):
    from treg.domain.tool_cache import (
        MAX_CACHE_BODY_BYTES,
        gc_expired_cache,
        lookup_cache,
        make_cache_key,
        store_cache,
    )
    from treg.models import ToolCacheRecord

    org = await _org_id(clients)

    # 1. Test cache key stability (query params sorted)
    k1 = make_cache_key(tool_id=1, method="GET", path="/data", query="b=2&a=1", body=b"")
    k2 = make_cache_key(tool_id=1, method="GET", path="/data", query="a=1&b=2", body=b"")
    assert k1 == k2

    tool_id = 99999
    # 2. Store and lookup
    async with session_maker() as db:
        cached = await store_cache(
            db,
            org_id=org,
            tool_id=tool_id,
            cache_key=k1,
            method="GET",
            path="/data",
            status_code=200,
            headers={"content-type": "application/json"},
            body=b'{"result": "cached_success"}',
            ttl_seconds=30,
        )
        assert cached is True
        await db.commit()

    async with session_maker() as db:
        hit = await lookup_cache(db, tool_id=tool_id, cache_key=k1)
        assert hit is not None
        assert hit.status_code == 200
        assert hit.response_body == b'{"result": "cached_success"}'
        assert "application/json" in hit.headers_json

    # 3. Test body size limit (> 1MB should not cache)
    large_body = b"x" * (MAX_CACHE_BODY_BYTES + 10)
    async with session_maker() as db:
        not_cached = await store_cache(
            db,
            org_id=org,
            tool_id=tool_id,
            cache_key="large_key",
            method="GET",
            path="/large",
            status_code=200,
            headers={},
            body=large_body,
            ttl_seconds=30,
        )
        assert not_cached is False

    # 4. Expired cache test and GC
    async with session_maker() as db:
        expired_rec = ToolCacheRecord(
            org_id=org,
            tool_id=tool_id,
            cache_key="expired_key",
            method="GET",
            path_url="/expired",
            status_code=200,
            headers_json="{}",
            response_body=b"expired",
            expires_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=5),
        )
        db.add(expired_rec)
        await db.commit()

    async with session_maker() as db:
        # Lookup expired key should return None
        expired_hit = await lookup_cache(db, tool_id=tool_id, cache_key="expired_key")
        assert expired_hit is None

        # GC should clean it up
        deleted_count = await gc_expired_cache(db)
        assert deleted_count >= 1
        await db.commit()


async def test_tool_create_and_update_with_cache_and_fallback(clients):
    org = await _org_id(clients)

    # 1. Create a backup tool
    resp1 = await clients.post(
        "/tools",
        json={
            "name": "backup-tool",
            "base_url": "https://api.backup.com",
        },
    )
    assert resp1.status_code == 200
    backup_id = resp1.json()["id"]

    # 2. Create primary tool with TTL cache and fallback
    resp2 = await clients.post(
        "/tools",
        json={
            "name": "primary-tool",
            "base_url": "https://api.primary.com",
            "cache_ttl_seconds": 300,
            "fallback_tool_id": backup_id,
        },
    )
    assert resp2.status_code == 200
    primary_data = resp2.json()
    assert primary_data["cache_ttl_seconds"] == 300
    assert primary_data["fallback_tool_id"] == backup_id
    primary_id = primary_data["id"]

    # 3. Update tool TTL cache
    patch_resp = await clients.patch(
        f"/tools/{primary_id}",
        json={"cache_ttl_seconds": 600},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["cache_ttl_seconds"] == 600
    assert patch_resp.json()["fallback_tool_id"] == backup_id


