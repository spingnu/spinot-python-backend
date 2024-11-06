from __future__ import annotations

from app.supabase_client import supabase


def get_report_by_id(report_id: int):
    response = (
        supabase.table("report").select("*").eq("id", report_id).limit(1).execute()
    )
    return response.data[0] if response.data else None
