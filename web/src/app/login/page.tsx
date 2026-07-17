"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { getBrowserClient } from "@/lib/supabase/client";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function oauthLogin(provider: "google" | "apple") {
    setBusy(true);
    setMessage(null);
    const supabase = getBrowserClient();
    const { error } = await supabase.auth.signInWithOAuth({
      provider,
      options: { redirectTo: `${window.location.origin}/auth/callback` },
    });
    if (error) {
      setMessage(error.message);
      setBusy(false);
    }
    // 成功時はプロバイダのページへリダイレクトされる
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setMessage(null);
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
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-sm flex-col justify-center gap-6 px-6">
      <h1 className="text-2xl font-bold">
        {mode === "login" ? "ログイン" : "アカウント作成"}
      </h1>

      <div className="flex flex-col gap-3">
        <button
          onClick={() => oauthLogin("google")}
          disabled={busy}
          className="flex items-center justify-center gap-2 rounded-lg border border-gray-300 py-3 font-medium transition hover:bg-gray-50 disabled:opacity-50"
        >
          Google でつづける
        </button>
        <button
          onClick={() => oauthLogin("apple")}
          disabled={busy}
          className="flex items-center justify-center gap-2 rounded-lg bg-black py-3 font-medium text-white transition hover:bg-gray-800 disabled:opacity-50"
        >
          Apple でつづける
        </button>
      </div>

      <div className="flex items-center gap-3 text-xs text-gray-400">
        <span className="h-px flex-1 bg-gray-200" />
        またはメールアドレスで
        <span className="h-px flex-1 bg-gray-200" />
      </div>

      <form onSubmit={submit} className="flex flex-col gap-4">
        <input
          type="email"
          required
          placeholder="メールアドレス"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="rounded-lg border border-gray-300 px-4 py-3"
        />
        <input
          type="password"
          required
          minLength={6}
          placeholder="パスワード (6文字以上)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="rounded-lg border border-gray-300 px-4 py-3"
        />
        <button
          type="submit"
          disabled={busy}
          className="rounded-lg bg-amber-600 py-3 font-semibold text-white transition hover:bg-amber-700 disabled:opacity-50"
        >
          {busy ? "処理中..." : mode === "login" ? "ログイン" : "登録する"}
        </button>
      </form>
      {message && <p className="text-sm text-red-600">{message}</p>}
      <button
        onClick={() => setMode(mode === "login" ? "signup" : "login")}
        className="text-sm text-gray-500 underline"
      >
        {mode === "login"
          ? "アカウントを作成する"
          : "既にアカウントをお持ちの方はこちら"}
      </button>
    </main>
  );
}
