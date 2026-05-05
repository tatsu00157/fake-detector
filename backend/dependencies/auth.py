from fastapi import Header, HTTPException, Depends
from supabase import create_client
from core.config import settings
from datetime import date

FREE_LIMIT = 10


def _supabase():
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


async def require_auth(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "認証が必要です")
    token = authorization[7:]
    try:
        user = _supabase().auth.get_user(token)
        return user.user
    except Exception:
        raise HTTPException(401, "無効なトークンです")


async def check_usage(user=Depends(require_auth)):
    sb = _supabase()
    today = str(date.today())
    uid = user.id

    result = sb.table("usage_logs").select("id, count").eq("user_id", uid).eq("date", today).execute()

    if result.data:
        row = result.data[0]
        if row["count"] >= FREE_LIMIT:
            raise HTTPException(429, "本日の無料利用回数（10回）を超えました")
        sb.table("usage_logs").update({"count": row["count"] + 1}).eq("id", row["id"]).execute()
    else:
        sb.table("usage_logs").insert({"user_id": uid, "date": today, "count": 1}).execute()

    return user
