import Link from "next/link";

export default function LandingPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-2xl flex-col items-center justify-center gap-8 px-6 text-center">
      <p className="text-sm font-medium tracking-widest text-amber-600">
        MEMORY KEEPER (仮)
      </p>
      <h1 className="text-4xl font-bold leading-tight">
        友だちとの思い出、
        <br />
        AIがぜんぶ覚えておきます。
      </h1>
      <p className="text-lg text-gray-500">
        一言メモするだけで、AIが「誰と・どこで・何をしたか」を整理。
        次に会うときに「前なに話したっけ?」と聞けば、すぐ思い出せます。
      </p>
      <Link
        href="/login"
        className="rounded-full bg-amber-600 px-8 py-3 font-semibold text-white transition hover:bg-amber-700"
      >
        無料ではじめる
      </Link>
      <p className="text-sm text-gray-400">
        無料で10件まで記録できます。月50円で無制限に。
      </p>
    </main>
  );
}
