from fastapi import Header, HTTPException, Depends
from supabase import create_client
from core.config import settings
from datetime import date
from typing import Optional

FREE_LIMIT = 10


def _is_premium(sb, user_id: str) -> bool:
    result = sb.table("subscriptions").select("status").eq("user_id", user_id).execute()
    if result.data and result.data[0].get("status") == "active":
        return True
    return False


def _supabase():
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


async def optional_auth(authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization[7:]
    try:
        user = _supabase().auth.get_user(token)
        return user.user
    except Exception:
        return None


async def check_usage(user=Depends(optional_auth)):
    if user is None:
        return None

    sb = _supabase()
    today = str(date.today())
    uid = user.id

    result = sb.table("usage_logs").select("id, count").eq("user_id", uid).eq("date", today).execute()

    if _is_premium(sb, uid):
        return user

    if result.data:
        row = result.data[0]
        if row["count"] >= FREE_LIMIT:
            raise HTTPException(429, "本日の無料利用回数（10回）を超えました")
        sb.table("usage_logs").update({"count": row["count"] + 1}).eq("id", row["id"]).execute()
    else:
        sb.table("usage_logs").insert({"user_id": uid, "date": today, "count": 1}).execute()

    return user
