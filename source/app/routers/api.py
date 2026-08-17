from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from sqlalchemy import text

from app.core.metrics import snapshot
from app.database import engine


router = APIRouter(
    prefix="/api/v1",
    tags=["api"],
)


@router.get("/health")
def health():
    database = "error"

    try:
        with engine.connect() as connection:
            connection.execute(
                text(
                    "SELECT 1"
                )
            )

        database = "ok"

    except Exception:
        pass

    return {
        "ok": database == "ok",
        "data": {
            "service": "srv-control",
            "database": database,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        },
        "error": (
            None
            if database == "ok"
            else "database unavailable"
        ),
    }


@router.get("/dashboard/metrics")
def dashboard_metrics():
    return {
        "ok": True,
        "data": snapshot(),
        "error": None,
    }


async def metric_event_stream():
    while True:
        try:
            payload = {
                "ok": True,
                "data": snapshot(),
                "error": None,
            }

            yield (
                "event: metrics\n"
                "data: "
                +
                json.dumps(
                    payload,
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                +
                "\n\n"
            )

        except asyncio.CancelledError:
            break

        except Exception as exc:
            payload = {
                "ok": False,
                "data": None,
                "error": str(exc)[:300],
            }

            yield (
                "event: metrics\n"
                "data: "
                +
                json.dumps(
                    payload,
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                +
                "\n\n"
            )

        await asyncio.sleep(2)


@router.get("/dashboard/stream")
async def dashboard_stream():
    return StreamingResponse(
        metric_event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
