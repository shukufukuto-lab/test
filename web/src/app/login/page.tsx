"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { getBrowserClient } from "@/lib/supabase/client";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState(false);
  const [busy, setBusy] = useState(false);

  async function oauthLogin(provider: "google" | "apple") {
    setBusy(true);
    setMessage(null);
    setError(false);
    const supabase = getBrowserClient();
    const { error } = await supabase.auth.signInWithOAuth({
      provider,
      options: { redirectTo: `${window.location.origin}/auth/callback` },
    });
    if (error) {
      setMessage(error.message);
      setError(true);
      setBusy(false);
    }
    // 成功時はプロバイダのページへリダイレクトされる
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setMessage(null);
    setError(false);
    const supabase = getBrowserClient();
    try {
      if (mode === "signup") {
        const { error } = await supabase.auth.signUp({ email, password });
        if (error) throw error;
        setMessage(
          "確認メールを送信しました。メール内のリンクを開いてからログインしてください。",
        );
      } else {
        const { error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (error) throw error;
        router.push("/app");
        router.refresh();
      }
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "エラーが発生しました");
      setError(true);
    } finally {
      setBusy(false);
    }
  }

  const inputClass =
    "rounded-xl border border-input-border bg-input px-4 py-3 outline-none transition placeholder:text-subtle focus:border-brand focus:ring-2 focus:ring-ring/40";

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-sm flex-col justify-center gap-7 px-6 py-12">
      <div className="text-center">
        <Link
          href="/"
          className="text-xs font-medium tracking-widest text-brand"
        >
          MEMORY KEEPER（仮）
        </Link>
        <h1 className="mt-4 text-2xl font-bold">
          {mode === "login" ? "おかえりなさい" : "アカウントを作成"}
        </h1>
        <p className="mt-1.5 text-sm text-muted">
          {mode === "login"
            ? "思い出のつづきを、ここから。"
            : "無料で10件まで、いますぐ始められます。"}
        </p>
      </div>

      <div className="rounded-2xl border border-card-border bg-card p-6 shadow-sm">
        <div className="flex flex-col gap-3">
          <button
            onClick={() => oauthLogin("google")}
            disabled={busy}
            className="flex items-center justify-center gap-2 rounded-xl border border-input-border bg-input py-3 font-medium transition hover:bg-brand-soft disabled:opacity-50"
          >
            Google でつづける
          </button>
          <button
            onClick={() => oauthLogin("apple")}
            disabled={busy}
            className="flex items-center justify-center gap-2 rounded-xl bg-black py-3 font-medium text-white transition hover:bg-gray-800 disabled:opacity-50"
          >
            Apple でつづける
          </button>
        </div>

        <div className="my-5 flex items-center gap-3 text-xs text-subtle">
          <span className="h-px flex-1 bg-card-border" />
          またはメールアドレスで
          <span className="h-px flex-1 bg-card-border" />
        </div>

        <form onSubmit={submit} className="flex flex-col gap-3">
          <input
            type="email"
            required
            placeholder="メールアドレス"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className={inputClass}
          />
          <input
            type="password"
            required
            minLength={6}
            placeholder="パスワード (6文字以上)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className={inputClass}
          />
          <button
            type="submit"
            disabled={busy}
            className="mt-1 rounded-xl bg-brand py-3 font-semibold text-brand-foreground transition hover:bg-brand-hover disabled:opacity-50"
          >
            {busy ? "処理中..." : mode === "login" ? "ログイン" : "登録する"}
          </button>
        </form>

        {message && (
          <p
            className={`mt-4 text-sm ${
              error ? "text-red-600" : "text-brand-soft-foreground"
            }`}
          >
            {message}
          </p>
        )}
      </div>

      <button
        onClick={() => {
          setMode(mode === "login" ? "signup" : "login");
          setMessage(null);
          setError(false);
        }}
        className="text-center text-sm text-muted transition hover:text-foreground"
      >
        {mode === "login" ? (
          <>
            アカウントをお持ちでない方は{" "}
            <span className="font-semibold text-brand">新規登録</span>
          </>
        ) : (
          <>
            既にアカウントをお持ちの方は{" "}
            <span className="font-semibold text-brand">ログイン</span>
          </>
        )}
      </button>
    </main>
  );
}
