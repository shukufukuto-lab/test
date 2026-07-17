import { NextResponse } from "next/server";
import Stripe from "stripe";
import { createAdminClient } from "@/lib/supabase/server";

export const dynamic = "force-dynamic";

// Stripe からのイベントを受けて profiles.subscription_status を同期する
export async function POST(req: Request) {
  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);
  const body = await req.text();
  const signature = req.headers.get("stripe-signature");
  if (!signature) {
    return NextResponse.json({ error: "missing signature" }, { status: 400 });
  }

  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!,
    );
  } catch {
    return NextResponse.json({ error: "invalid signature" }, { status: 400 });
  }

  const supabase = createAdminClient();

  async function setStatus(customerId: string, status: string) {
    await supabase
      .from("profiles")
      .update({ subscription_status: status })
      .eq("stripe_customer_id", customerId);
  }

  switch (event.type) {
    case "checkout.session.completed": {
      const session = event.data.object;
      if (session.customer) await setStatus(session.customer as string, "active");
      break;
    }
    case "customer.subscription.updated": {
      const sub = event.data.object;
      const status =
        sub.status === "active" || sub.status === "trialing" ? "active" : "canceled";
      await setStatus(sub.customer as string, status);
      break;
    }
    case "customer.subscription.deleted": {
      const sub = event.data.object;
      await setStatus(sub.customer as string, "canceled");
      break;
    }
  }

  return NextResponse.json({ received: true });
}
