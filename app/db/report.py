from __future__ import annotations

from datetime import datetime

from app.supabase_client import supabase


def get_report_by_id(report_id: int):
    response = (
        supabase.table("report").select("*").eq("id", report_id).limit(1).execute()
    )
    return response.data[0] if response.data else None


def update_report_for_user_on_date(user_id: str, date: datetime, report: str):
    date = date.replace(hour=0, minute=0, second=0, microsecond=0)

    response = (
        supabase.table("report")
        .upsert({"user_id": user_id, "date": date.isoformat(), "report": report})
        .execute()
    )
    return response.data
