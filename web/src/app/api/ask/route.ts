import Anthropic from "@anthropic-ai/sdk";
import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const { question } = (await req.json()) as { question?: string };
  if (!question?.trim()) {
    return NextResponse.json({ error: "question is required" }, { status: 400 });
  }

  // 直近の記録を文脈として渡す (MVP は全件検索。将来は人物スコープの検索に置き換える)
  const { data: memories, error } = await supabase
    .from("memories")
    .select("raw_text, people, place, occurred_on, summary")
    .order("created_at", { ascending: false })
    .limit(50);
  if (error) return NextResponse.json({ error: error.message }, { status: 500 });

  if (!memories || memories.length === 0) {
    return NextResponse.json({
      answer: "まだ記録がありません。まずは思い出を記録してみてください。",
    });
  }

  const context = memories
    .map(
      (m) =>
        `- ${m.occurred_on ?? "日付不明"} / ${m.people.join("、") || "人物不明"} / ${
          m.place ?? "場所不明"
        }: ${m.summary ?? m.raw_text}`,
    )
    .join("\n");

  const anthropic = new Anthropic();
  const response = await anthropic.messages.create({
    model: "claude-haiku-4-5",
    max_tokens: 1024,
    system:
      "あなたはユーザーの「思い出の記憶係」です。以下はユーザーが記録した思い出の一覧です。" +
      "質問に対して、この記録だけを根拠に、親しみやすい日本語で簡潔に答えてください。" +
      "記録にないことは「記録には見つからない」と正直に伝えてください。\n\n" +
      `<memories>\n${context}\n</memories>`,
    messages: [{ role: "user", content: question }],
  });

  if (response.stop_reason === "refusal") {
    return NextResponse.json({ error: "llm_refused" }, { status: 422 });
  }
  const answer =
    response.content.find((b) => b.type === "text")?.text ??
    "回答を生成できませんでした。";
  return NextResponse.json({ answer });
}
