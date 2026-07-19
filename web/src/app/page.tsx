import Link from "next/link";

const features = [
  {
    icon: "✍️",
    title: "一言で、記録",
    body: "「昨日 太郎と下北で飲んだ」——それだけ。AIが誰と・どこで・何をしたかを整理して残します。",
  },
  {
    icon: "💬",
    title: "自然文で、思い出す",
    body: "「太郎と最後に会ったのいつ?」と聞くだけ。蓄積した記録を根拠にAIが答えます。",
  },
  {
    icon: "🔔",
    title: "AIから、そっと",
    body: "「1年前の今日、○○と…」——振り返る習慣がなくても、思い出のほうから会いに来ます。",
  },
];

const steps = [
  { n: "1", text: "その日あったことを一言メモ" },
  { n: "2", text: "AIが人物・場所・出来事に整理" },
  { n: "3", text: "次に会う前に、文脈ごと思い出す" },
];

export default function LandingPage() {
  return (
    <div className="flex flex-1 flex-col">
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-x-0 -top-32 h-72 bg-gradient-to-b from-brand-soft to-transparent opacity-70 blur-2xl"
        />
        <main className="relative mx-auto flex max-w-2xl flex-col items-center gap-7 px-6 pt-24 pb-16 text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-card-border bg-card px-4 py-1.5 text-xs font-medium tracking-widest text-brand shadow-sm">
            MEMORY KEEPER（仮）
          </span>
          <h1 className="text-4xl font-bold leading-tight sm:text-5xl">
            友だちとの思い出、
            <br />
            <span className="text-brand">AIがぜんぶ覚えておきます。</span>
          </h1>
          <p className="max-w-xl text-lg leading-relaxed text-muted">
            一言メモするだけで、AIが「誰と・どこで・何をしたか」を整理。
            次に会うときに「前なに話したっけ?」と聞けば、すぐ思い出せます。
          </p>
          <div className="flex flex-col items-center gap-3">
            <Link
              href="/login"
              className="rounded-full bg-brand px-8 py-3.5 font-semibold text-brand-foreground shadow-sm transition hover:bg-brand-hover hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
            >
              無料ではじめる
            </Link>
            <p className="text-sm text-subtle">
              無料で10件まで記録できます。月50円で無制限に。
            </p>
          </div>
        </main>
      </section>

      {/* Features */}
      <section className="mx-auto w-full max-w-4xl px-6 py-12">
        <div className="grid gap-5 sm:grid-cols-3">
          {features.map((f) => (
            <div
              key={f.title}
              className="rounded-2xl border border-card-border bg-card p-6 text-left shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
            >
              <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-xl bg-brand-soft text-xl">
                {f.icon}
              </div>
              <h3 className="mb-2 font-semibold">{f.title}</h3>
              <p className="text-sm leading-relaxed text-muted">{f.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="mx-auto w-full max-w-2xl px-6 py-12">
        <h2 className="mb-8 text-center text-sm font-semibold tracking-widest text-subtle">
          つかいかた
        </h2>
        <ol className="flex flex-col gap-4">
          {steps.map((s) => (
            <li
              key={s.n}
              className="flex items-center gap-4 rounded-2xl border border-card-border bg-card px-5 py-4 shadow-sm"
            >
              <span className="flex h-9 w-9 flex-none items-center justify-center rounded-full bg-brand text-sm font-bold text-brand-foreground">
                {s.n}
              </span>
              <span className="text-sm sm:text-base">{s.text}</span>
            </li>
          ))}
        </ol>
      </section>

      {/* Closing CTA */}
      <section className="mx-auto w-full max-w-2xl px-6 pt-8 pb-24 text-center">
        <div className="rounded-3xl border border-card-border bg-card px-8 py-12 shadow-sm">
          <h2 className="text-2xl font-bold">
            大切な人との時間を、
            <br className="sm:hidden" />
            なかったことにしない。
          </h2>
          <p className="mx-auto mt-3 max-w-md text-sm leading-relaxed text-muted">
            記録は完全に個人用・非公開。あなたと、あなたの思い出だけのための場所です。
          </p>
          <Link
            href="/login"
            className="mt-7 inline-block rounded-full bg-brand px-8 py-3.5 font-semibold text-brand-foreground shadow-sm transition hover:bg-brand-hover hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
          >
            無料ではじめる
          </Link>
        </div>
      </section>

      <footer className="border-t border-card-border py-8 text-center text-xs text-subtle">
        Memory Keeper（仮）· 完全個人用・非公開の思い出記録サービス
      </footer>
    </div>
  );
}
