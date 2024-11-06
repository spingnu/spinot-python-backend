from __future__ import annotations

from datetime import datetime

from app.supabase_client import supabase


def get_report_by_id(report_id: int):
    response = (
        supabase.table("report").select("*").eq("id", report_id).limit(1).execute()
    )
    return response.data[0] if response.data else None


def update_report_for_user_on_date(
    user_id: str, date: datetime, report: str, reference: dict
):
    date = date.replace(hour=0, minute=0, second=0, microsecond=0)

    # check if there is report with same date and user_id in db then update it
    response = (
        supabase.table("report")
        .select("id")
        .eq("user_id", user_id)
        .eq("date", date.isoformat())
        .limit(1)
        .execute()
    )

    if response.data:
        report_id = response.data[0]["id"]
        response = (
            supabase.table("report")
            .update({"report": report, "reference": reference})
            .eq("id", report_id)
            .execute()
        )
        return response.data
    else:
        response = (
            supabase.table("report")
            .insert(
                {
                    "user_id": user_id,
                    "date": date.isoformat(),
                    "report": report,
                    "reference": reference,
                }
            )
            .execute()
        )
    return response.data
