import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import MemoryApp from "./memory-app";

export const dynamic = "force-dynamic";

export default async function AppPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  const { data: profile } = await supabase
    .from("profiles")
    .select("subscription_status")
    .eq("id", user.id)
    .single();

  return (
    <MemoryApp
      email={user.email ?? ""}
      subscriptionStatus={profile?.subscription_status ?? "free"}
    />
  );
}
