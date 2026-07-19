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

const FREE_LIMIT = 10;

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
  const [notice, setNotice] = useState<{
    text: string;
    tone: "info" | "error";
  } | null>(null);

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
        setNotice({
          text: "無料枠 (10件) に達しました。月50円のプランで無制限に記録できます。",
          tone: "info",
        });
        return;
      }
      if (!res.ok) throw new Error("記録に失敗しました");
      setRecordText("");
      setNotice({ text: "記録しました!", tone: "info" });
      await loadMemories();
    } catch (err) {
      setNotice({
        text: err instanceof Error ? err.message : "エラーが発生しました",
        tone: "error",
      });
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

  const used = memories.length;
  const remaining = Math.max(0, FREE_LIMIT - used);
  const usagePct = Math.min(100, (used / FREE_LIMIT) * 100);

  return (
    <div className="flex flex-1 flex-col">
      <header className="sticky top-0 z-10 border-b border-card-border bg-background/80 backdrop-blur">
        <div className="mx-auto flex max-w-2xl items-center justify-between px-4 py-3.5">
          <span className="font-bold text-brand">Memory Keeper（仮）</span>
          <div className="flex items-center gap-3 text-sm">
            <span
              className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                isPro
                  ? "bg-brand-soft text-brand-soft-foreground"
                  : "bg-card text-subtle ring-1 ring-card-border"
              }`}
            >
              {isPro ? "Pro" : "Free"}
            </span>
            <span className="hidden text-muted sm:inline">{email}</span>
            <button
              onClick={signOut}
              className="text-subtle transition hover:text-foreground"
            >
              ログアウト
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto w-full max-w-2xl flex-1 px-4 py-8">
        {!isPro && (
          <div className="mb-6 rounded-2xl border border-card-border bg-card p-4 shadow-sm">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-sm font-semibold">
                  無料枠 {used}/{FREE_LIMIT} 件
                </p>
                <p className="mt-0.5 text-xs text-muted">
                  {remaining > 0
                    ? `あと${remaining}件記録できます。月50円で無制限に。`
                    : "上限に達しました。月50円で無制限に。"}
                </p>
              </div>
              <button
                onClick={upgrade}
                disabled={busy}
                className="flex-none rounded-full bg-brand px-4 py-2 text-sm font-semibold text-brand-foreground transition hover:bg-brand-hover disabled:opacity-50"
              >
                アップグレード
              </button>
            </div>
            <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-brand-soft">
              <div
                className="h-full rounded-full bg-brand transition-all"
                style={{ width: `${usagePct}%` }}
              />
            </div>
          </div>
        )}

        {/* Segmented tabs */}
        <div className="mb-6 grid grid-cols-2 gap-1 rounded-full border border-card-border bg-card p-1 shadow-sm">
          {(["record", "recall"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`rounded-full py-2 text-sm font-semibold transition ${
                tab === t
                  ? "bg-brand text-brand-foreground shadow-sm"
                  : "text-muted hover:text-foreground"
              }`}
            >
              {t === "record" ? "記録する" : "思い出す"}
            </button>
          ))}
        </div>

        {tab === "record" ? (
          <section className="flex flex-col gap-3">
            <textarea
              value={recordText}
              onChange={(e) => setRecordText(e.target.value)}
              rows={3}
              placeholder="例: 昨日 太郎と下北沢で飲んだ。転職の相談をされた"
              className="resize-none rounded-2xl border border-input-border bg-input px-4 py-3 outline-none transition placeholder:text-subtle focus:border-brand focus:ring-2 focus:ring-ring/40"
            />
            <button
              onClick={record}
              disabled={busy || !recordText.trim()}
              className="self-end rounded-full bg-brand px-6 py-2.5 font-semibold text-brand-foreground transition hover:bg-brand-hover disabled:opacity-50"
            >
              {busy ? "AIが整理中..." : "記録する"}
            </button>
          </section>
        ) : (
          <section className="flex flex-col gap-3">
            <div className="flex gap-2">
              <input
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="例: 太郎と最後に会ったのいつだっけ?"
                className="flex-1 rounded-full border border-input-border bg-input px-5 py-3 outline-none transition placeholder:text-subtle focus:border-brand focus:ring-2 focus:ring-ring/40"
                onKeyDown={(e) => e.key === "Enter" && !busy && ask()}
              />
              <button
                onClick={ask}
                disabled={busy || !question.trim()}
                className="flex-none rounded-full bg-brand px-6 py-2.5 font-semibold text-brand-foreground transition hover:bg-brand-hover disabled:opacity-50"
              >
                {busy ? "..." : "聞く"}
              </button>
            </div>
            {answer && (
              <div className="flex gap-3 rounded-2xl border border-card-border bg-brand-soft px-4 py-3.5">
                <span className="text-lg leading-none">💬</span>
                <p className="whitespace-pre-wrap text-sm leading-relaxed text-brand-soft-foreground">
                  {answer}
                </p>
              </div>
            )}
          </section>
        )}

        {notice && (
          <p
            className={`mt-4 text-sm ${
              notice.tone === "error" ? "text-red-600" : "text-brand-soft-foreground"
            }`}
          >
            {notice.text}
          </p>
        )}

        <section className="mt-10">
          <h2 className="mb-3 text-sm font-semibold text-muted">
            最近の思い出（{used}件）
          </h2>
          <ul className="flex flex-col gap-3">
            {memories.map((m) => (
              <li
                key={m.id}
                className="rounded-2xl border border-card-border bg-card px-4 py-3.5 shadow-sm transition hover:shadow-md"
              >
                <p className="text-sm font-medium leading-relaxed">
                  {m.summary ?? m.raw_text}
                </p>
                <div className="mt-2 flex flex-wrap items-center gap-1.5 text-xs">
                  <span className="text-subtle">
                    {m.occurred_on ?? "日付不明"}
                  </span>
                  {m.people.map((p) => (
                    <span
                      key={p}
                      className="rounded-full bg-brand-soft px-2 py-0.5 font-medium text-brand-soft-foreground"
                    >
                      {p}
                    </span>
                  ))}
                  {m.place && (
                    <span className="rounded-full bg-card px-2 py-0.5 text-muted ring-1 ring-card-border">
                      📍 {m.place}
                    </span>
                  )}
                </div>
              </li>
            ))}
            {memories.length === 0 && (
              <li className="rounded-2xl border border-dashed border-card-border px-4 py-10 text-center">
                <p className="text-2xl">🕊️</p>
                <p className="mt-2 text-sm text-muted">
                  まだ記録がありません。
                  <br />
                  「記録する」から最初の思い出を残してみましょう。
                </p>
              </li>
            )}
          </ul>
        </section>
      </main>
    </div>
  );
}
