import stripe
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from core.config import settings
from dependencies.auth import require_auth

router = APIRouter(tags=["stripe"])


def _stripe():
    stripe.api_key = settings.stripe_secret_key
    return stripe


@router.post("/stripe/checkout")
async def create_checkout_session(user=Depends(require_auth)):
    s = _stripe()
    try:
        session = s.checkout.Session.create(
            customer_email=user.email,
            metadata={"user_id": user.id},
            line_items=[{"price": settings.stripe_price_id, "quantity": 1}],
            mode="subscription",
            subscription_data={"metadata": {"user_id": user.id}},
            success_url="http://localhost:3000/pricing?success=true",
            cancel_url="http://localhost:3000/pricing?canceled=true",
        )
        return {"url": session.url}
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/stripe/portal")
async def create_portal_session(user=Depends(require_auth)):
    s = _stripe()
    sb = __import__("supabase").create_client(settings.supabase_url, settings.supabase_service_role_key)
    result = sb.table("subscriptions").select("stripe_customer_id").eq("user_id", user.id).execute()

    if not result.data or not result.data[0].get("stripe_customer_id"):
        raise HTTPException(404, "サブスクリプションが見つかりません")

    customer_id = result.data[0]["stripe_customer_id"]
    session = s.billing_portal.Session.create(
        customer=customer_id,
        return_url="http://localhost:3000/",
    )
    return {"url": session.url}


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    print(f"[webhook] secret length={len(settings.stripe_webhook_secret)} starts_with={settings.stripe_webhook_secret[:10]}")
    print(f"[webhook] payload length={len(payload)}")
    print(f"[webhook] sig_header={sig_header}")
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except Exception as e:
        print(f"Webhook error: {e}")
        raise HTTPException(400, str(e))

    _stripe()
    sb = __import__("supabase").create_client(settings.supabase_url, settings.supabase_service_role_key)

    if event["type"] in ("customer.subscription.created", "customer.subscription.updated"):
        sub = event["data"]["object"]
        customer_id = sub["customer"]
        status = sub["status"]
        user_id = sub.get("metadata", {}).get("user_id")

        if not user_id:
            customer = stripe.Customer.retrieve(customer_id)
            user_id = customer.get("metadata", {}).get("user_id")

        if user_id:
            sb.table("subscriptions").upsert({
                "user_id": user_id,
                "stripe_customer_id": customer_id,
                "stripe_subscription_id": sub["id"],
                "status": status,
                "current_period_end": sub["current_period_end"],
            }, on_conflict="user_id").execute()

    elif event["type"] == "customer.subscription.deleted":
        sub = event["data"]["object"]
        sb.table("subscriptions").update({"status": "canceled"}).eq(
            "stripe_subscription_id", sub["id"]
        ).execute()

    return JSONResponse({"status": "ok"})
