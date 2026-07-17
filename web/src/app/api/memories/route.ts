import Anthropic from "@anthropic-ai/sdk";
import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

export const dynamic = "force-dynamic";

const FREE_MEMORY_LIMIT = 10;

const extractionSchema = {
  type: "object",
  properties: {
    people: {
      type: "array",
      items: { type: "string" },
      description: "一緒にいた人の名前・呼び名。いなければ空配列",
    },
    place: { type: ["string", "null"], description: "場所。不明なら null" },
    occurred_on: {
      type: ["string", "null"],
      format: "date",
      description: "出来事の日付 (YYYY-MM-DD)。不明なら null",
    },
    summary: { type: "string", description: "出来事の一言要約 (30字以内)" },
  },
  required: ["people", "place", "occurred_on", "summary"],
  additionalProperties: false,
} as const;

export async function GET() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const { data, error } = await supabase
    .from("memories")
    .select("id, raw_text, people, place, occurred_on, summary, created_at")
    .order("created_at", { ascending: false })
    .limit(50);
  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json({ memories: data });
}

export async function POST(req: Request) {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const { text } = (await req.json()) as { text?: string };
  if (!text?.trim()) {
    return NextResponse.json({ error: "text is required" }, { status: 400 });
  }

  // 無料枠は記録件数に上限を設ける (サブスク加入で解除)
  const { data: profile } = await supabase
    .from("profiles")
    .select("subscription_status")
    .eq("id", user.id)
    .single();
  if (profile?.subscription_status !== "active") {
    const { count } = await supabase
      .from("memories")
      .select("id", { count: "exact", head: true });
    if ((count ?? 0) >= FREE_MEMORY_LIMIT) {
      return NextResponse.json(
        { error: "free_limit_reached", limit: FREE_MEMORY_LIMIT },
        { status: 402 },
      );
    }
  }

  // Claude (Haiku 4.5) で 5W1H を構造化する。
  // コスト設計 (docs/SPEC.md) に基づき会話系は Haiku を使う。
  const anthropic = new Anthropic();
  const today = new Date().toISOString().slice(0, 10);
  const response = await anthropic.messages.create({
    model: "claude-haiku-4-5",
    max_tokens: 1024,
    system:
      `あなたは思い出記録アプリの構造化エンジンです。今日の日付は ${today} です。` +
      "ユーザーの入力から、誰と・どこで・いつ・何をしたかを抽出してください。" +
      "「昨日」「先週金曜」のような相対日付は今日の日付から具体的な日付に変換してください。",
    messages: [{ role: "user", content: text }],
    output_config: {
      format: { type: "json_schema", schema: extractionSchema },
    },
  });

  if (response.stop_reason === "refusal") {
    return NextResponse.json({ error: "llm_refused" }, { status: 422 });
  }
  const jsonText = response.content.find((b) => b.type === "text")?.text ?? "{}";
  const extracted = JSON.parse(jsonText) as {
    people: string[];
    place: string | null;
    occurred_on: string | null;
    summary: string;
  };

  const { data, error } = await supabase
    .from("memories")
    .insert({
      user_id: user.id,
      raw_text: text,
      people: extracted.people,
      place: extracted.place,
      occurred_on: extracted.occurred_on,
      summary: extracted.summary,
    })
    .select()
    .single();
  if (error) return NextResponse.json({ error: error.message }, { status: 500 });

  return NextResponse.json({ memory: data });
}
