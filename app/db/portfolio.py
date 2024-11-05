from __future__ import annotations

from app.supabase_client import supabase


def get_user_portfolio(user_id: str):
    response = (
        supabase.table("portfolio").select("assets(*)").eq("user_id", user_id).execute()
    ).data

    data = [portfolio["assets"] for portfolio in response]

    return data


def filter_out_user_without_portfolio(user_ids: list[str]):
    user_ids_with_portfolio = []
    for user_id in user_ids:
        portfolio = get_user_portfolio(user_id)
        if len(portfolio) > 0:
            user_ids_with_portfolio.append(user_id)

    return user_ids_with_portfolio


if __name__ == "__main__":
    user_id = "b447cb9c-39f3-4e72-82bf-932dbf9204a5"
    portfolio = get_user_portfolio(user_id)
    print(portfolio)
    print(f"Found {len(portfolio)} assets in user's portfolio")
