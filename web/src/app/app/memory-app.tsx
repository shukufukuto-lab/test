"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { getBrowserClient } from "@/lib/supabase/client";

type Memory = {
  id: string;
  raw_text: string;
  people: string[];
  place: string | null;
  occurred_on: string | null;
  summary: string | null;
  created_at: string;
};

export default function MemoryApp({
  email,
  subscriptionStatus,
}: {
  email: string;
  subscriptionStatus: string;
}) {
  const router = useRouter();
  const [tab, setTab] = useState<"record" | "recall">("record");
  const [memories, setMemories] = useState<Memory[]>([]);
  const [recordText, setRecordText] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  const isPro = subscriptionStatus === "active";

  const loadMemories = useCallback(async () => {
    const res = await fetch("/api/memories");
    if (res.ok) {
      const data = await res.json();
      setMemories(data.memories ?? []);
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const res = await fetch("/api/memories");
      if (res.ok && !cancelled) {
        const data = await res.json();
        setMemories(data.memories ?? []);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  async function record() {
    if (!recordText.trim()) return;
    setBusy(true);
    setNotice(null);
    try {
      const res = await fetch("/api/memories", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: recordText }),
      });
      if (res.status === 402) {
        setNotice(
          "無料枠 (10件) に達しました。月50円のプランで無制限に記録できます。",
        );
        return;
      }
      if (!res.ok) throw new Error("記録に失敗しました");
      setRecordText("");
      setNotice("記録しました!");
      await loadMemories();
    } catch (err) {
      setNotice(err instanceof Error ? err.message : "エラーが発生しました");
    } finally {
      setBusy(false);
    }
  }

  async function ask() {
    if (!question.trim()) return;
    setBusy(true);
    setAnswer(null);
    try {
      const res = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      if (!res.ok) throw new Error("回答の生成に失敗しました");
      const data = await res.json();
      setAnswer(data.answer);
    } catch (err) {
      setAnswer(err instanceof Error ? err.message : "エラーが発生しました");
    } finally {
      setBusy(false);
    }
  }

  async function upgrade() {
    setBusy(true);
    try {
      const res = await fetch("/api/stripe/checkout", { method: "POST" });
      const data = await res.json();
      if (data.url) window.location.href = data.url;
    } finally {
      setBusy(false);
    }
  }

  async function signOut() {
    await getBrowserClient().auth.signOut();
    router.push("/");
    router.refresh();
  }

  return (
    <main className="mx-auto min-h-screen max-w-2xl px-4 py-8">
      <header className="mb-8 flex items-center justify-between">
        <h1 className="text-xl font-bold text-amber-700">Memory Keeper (仮)</h1>
        <div className="flex items-center gap-3 text-sm">
          <span className="text-gray-500">{email}</span>
          <span
            className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
              isPro ? "bg-amber-100 text-amber-700" : "bg-gray-100 text-gray-500"
            }`}
          >
            {isPro ? "Pro" : "Free"}
          </span>
          <button onClick={signOut} className="text-gray-400 underline">
            ログアウト
          </button>
        </div>
      </header>

      {!isPro && (
        <div className="mb-6 flex items-center justify-between rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm">
          <span>
            記録 {memories.length}/10 件 (無料枠) — 月50円で無制限に
          </span>
          <button
            onClick={upgrade}
            disabled={busy}
            className="rounded-full bg-amber-600 px-4 py-1.5 font-semibold text-white hover:bg-amber-700 disabled:opacity-50"
          >
            アップグレード
          </button>
        </div>
      )}

      <div className="mb-6 flex gap-2">
        <button
          onClick={() => setTab("record")}
          className={`rounded-full px-5 py-2 text-sm font-semibold ${
            tab === "record" ? "bg-amber-600 text-white" : "bg-gray-100 text-gray-600"
          }`}
        >
          記録する
        </button>
        <button
          onClick={() => setTab("recall")}
          className={`rounded-full px-5 py-2 text-sm font-semibold ${
            tab === "recall" ? "bg-amber-600 text-white" : "bg-gray-100 text-gray-600"
          }`}
        >
          思い出す
        </button>
      </div>

      {tab === "record" ? (
        <section className="flex flex-col gap-4">
          <textarea
            value={recordText}
            onChange={(e) => setRecordText(e.target.value)}
            rows={3}
            placeholder="例: 昨日 太郎と下北沢で飲んだ。転職の相談をされた"
            className="rounded-xl border border-gray-300 px-4 py-3"
          />
          <button
            onClick={record}
            disabled={busy || !recordText.trim()}
            className="self-end rounded-full bg-amber-600 px-6 py-2 font-semibold text-white hover:bg-amber-700 disabled:opacity-50"
          >
            {busy ? "AIが整理中..." : "記録する"}
          </button>
        </section>
      ) : (
        <section className="flex flex-col gap-4">
          <div className="flex gap-2">
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="例: 太郎と最後に会ったのいつだっけ?"
              className="flex-1 rounded-xl border border-gray-300 px-4 py-3"
              onKeyDown={(e) => e.key === "Enter" && !busy && ask()}
            />
            <button
              onClick={ask}
              disabled={busy || !question.trim()}
              className="rounded-full bg-amber-600 px-6 py-2 font-semibold text-white hover:bg-amber-700 disabled:opacity-50"
            >
              {busy ? "..." : "聞く"}
            </button>
          </div>
          {answer && (
            <div className="whitespace-pre-wrap rounded-xl bg-amber-50 px-4 py-3 text-sm leading-relaxed">
              {answer}
            </div>
          )}
        </section>
      )}

      {notice && <p className="mt-4 text-sm text-amber-700">{notice}</p>}

      <section className="mt-10">
        <h2 className="mb-3 text-sm font-semibold text-gray-500">
          最近の思い出 ({memories.length}件)
        </h2>
        <ul className="flex flex-col gap-3">
          {memories.map((m) => (
            <li key={m.id} className="rounded-xl border border-gray-200 px-4 py-3">
              <p className="text-sm font-medium">{m.summary ?? m.raw_text}</p>
              <p className="mt-1 text-xs text-gray-400">
                {m.occurred_on ?? "日付不明"} / {m.people.join("、") || "人物未記録"}
                {m.place ? ` / ${m.place}` : ""}
              </p>
            </li>
          ))}
          {memories.length === 0 && (
            <li className="text-sm text-gray-400">
              まだ記録がありません。「記録する」から最初の思い出を残してみましょう。
            </li>
          )}
        </ul>
      </section>
    </main>
  );
}
