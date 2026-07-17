# Memory Keeper (仮) — MVP

友だちとの思い出を一言メモで記録し、AIが「誰と・どこで・何をしたか」を構造化。
後から自然文で質問して思い出せる Web アプリの MVP です。

コンセプトの詳細は [`../docs/SPEC.md`](../docs/SPEC.md) を参照。

## 技術スタック

| 役割 | 技術 |
|---|---|
| フレームワーク | Next.js 16 (App Router) + React 19 + TypeScript |
| スタイリング | Tailwind CSS 4 |
| 認証 + DB | Supabase (メール認証 / Postgres + RLS) |
| 決済 | Stripe (Checkout + Webhook、月50円サブスク) |
| LLM | Claude API — `claude-haiku-4-5` (コスト設計に基づく) |
| ホスティング | Cloudflare Workers (@opennextjs/cloudflare) |

## 機能 (MVP スコープ)

- メール + パスワードでのサインアップ / ログイン
- **記録**: 自由文を投稿すると Claude が 5W1H (人物・場所・日付・要約) を構造化して保存
- **思い出す**: 「太郎と最後に会ったのいつ?」のような質問に、蓄積した記録を根拠に回答
- **課金**: 無料枠は記録10件まで。Stripe Checkout で月50円プランに加入すると無制限
- RLS により記録は本人しか読み書きできない (完全個人用・非公開の方針)

## セットアップ

### 1. Supabase

1. [supabase.com](https://supabase.com) でプロジェクト作成
2. SQL Editor で [`supabase/schema.sql`](./supabase/schema.sql) を実行
3. Authentication → Providers で Email を有効化 (開発中は「Confirm email」をオフにすると楽)
4. Project Settings → API から URL / anon key / service_role key を控える

#### ソーシャルログイン (Google / Apple)

Authentication → Providers で各プロバイダを有効化する。リダイレクト URL には
Supabase が表示する `https://<project>.supabase.co/auth/v1/callback` を各プロバイダ側に登録する。

- **Google**: [Google Cloud Console](https://console.cloud.google.com) で OAuth クライアント ID を作成し、Client ID / Secret を Supabase に設定
- **Apple**: [Apple Developer Program](https://developer.apple.com/programs/) (**年99ドルの有料登録が必要**) で Services ID + キーを作成し Supabase に設定。PoC 段階では後回しでも UI 上のボタンはエラー表示になるだけで他機能に影響なし
- **LINE**: Supabase の標準プロバイダに **LINE は含まれていない**ため未実装。本サービスは将来 LINE Bot 入口を持つ計画のため、その際に LINE Login (OIDC) を独自実装して Supabase の外部 JWT 連携で繋ぐ方針 (docs/SPEC.md 参照)

### 2. Stripe

1. [dashboard.stripe.com](https://dashboard.stripe.com) (テストモード) で商品を作成
   - 価格: **¥50 / 月** (継続課金) → Price ID (`price_...`) を控える
2. Developers → Webhooks でエンドポイントを追加
   - URL: `https://<デプロイ先>/api/stripe/webhook`
   - イベント: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`
   - Signing secret (`whsec_...`) を控える
   - ローカル開発では `stripe listen --forward-to localhost:3000/api/stripe/webhook`

### 3. Anthropic

[platform.claude.com](https://platform.claude.com) で API キーを発行。

### 4. 環境変数

```bash
cp .env.example .env.local
# 各値を埋める
```

### 5. 起動

```bash
npm install
npm run dev
# http://localhost:3000
```

## デプロイ (Cloudflare Workers)

無料枠で商用利用可 (1日10万リクエストまで)。[@opennextjs/cloudflare](https://opennext.js.org/cloudflare)
アダプタを導入済みで、設定は `wrangler.jsonc` / `open-next.config.ts` にある。

```bash
# 1. Cloudflare アカウントでログイン (初回のみ。ブラウザが開く)
npx wrangler login

# 2. サーバー側シークレットを登録 (初回のみ)
npx wrangler secret put ANTHROPIC_API_KEY
npx wrangler secret put STRIPE_SECRET_KEY
npx wrangler secret put STRIPE_WEBHOOK_SECRET
npx wrangler secret put STRIPE_PRICE_ID
npx wrangler secret put SUPABASE_SERVICE_ROLE_KEY

# 3. NEXT_PUBLIC_* はビルド時に埋め込まれるため .env に置く
#    (NEXT_PUBLIC_SUPABASE_URL / NEXT_PUBLIC_SUPABASE_ANON_KEY / NEXT_PUBLIC_APP_URL)
cp .env.example .env  # 値を埋める

# 4. デプロイ
npm run deploy
# → https://memory-keeper.<account>.workers.dev が発行される

# ローカルで Workers ランタイム込みの動作確認をしたい場合
npm run preview
```

デプロイ後にやること:

1. 発行された URL を `.env` の `NEXT_PUBLIC_APP_URL` に設定して再デプロイ
2. Stripe Webhook のエンドポイント URL を `https://<発行URL>/api/stripe/webhook` に設定
3. Supabase の Authentication → URL Configuration の Site URL / Redirect URLs に発行 URL を追加

## 構成

```
src/
  app/
    page.tsx              # ランディング
    login/page.tsx        # サインアップ / ログイン
    app/page.tsx          # メイン画面 (要ログイン)
    app/memory-app.tsx    # 記録 / 思い出す UI
    api/
      memories/route.ts   # GET: 一覧 / POST: 記録 (Claude で構造化)
      ask/route.ts        # POST: 質問に記録を根拠として回答
      stripe/checkout/route.ts  # Checkout セッション作成
      stripe/webhook/route.ts   # サブスク状態の同期
  lib/supabase/           # Supabase クライアント (browser / server / admin)
supabase/schema.sql       # DB スキーマ + RLS + トリガー
```

## MVP の割り切り (今後の課題)

- 振り返りは直近50件を全件文脈に載せる方式 → 将来は人物スコープ検索に置き換え
- リマインド機能 (LINE 通知等) は未実装
- 構造化はリアルタイム実行 → コスト最適化するなら Batch API 化
- 解約導線は Stripe Customer Portal 未接続 (ダッシュボードから手動)
