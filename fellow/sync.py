"""
ファイルサーバー同期モジュール

前提:
- マスタ(案件・要員・計画)はファイルサーバー上のCSVが正。全員が読み込むだけ。
  書き込みは管理者操作(案件マスタ/要員マスタ/計画工数登録画面での保存)時のみ、
  ローカルDB更新に加えてファイルサーバーへも書き戻す。
- 実績(タイマー・手動入力)は「1人1ファイル」の原則。
  自分のファイルだけ書き込み、他人のファイルは読み込み専用(チーム集計用)。
- ネットワーク切断時はローカルDBのキャッシュで動作し、次回接続時に同期する。
"""

import csv
import io
import os
from datetime import datetime
from pathlib import Path

import db

# 環境に応じて設定ファイル等から注入することを想定(ひとまず既定値)
FILESERVER_ROOT = Path(os.environ.get("FELLOW_FILESERVER_ROOT", r"\\fileserver\fellow"))
MASTERS_DIR = FILESERVER_ROOT / "masters"
ACTUALS_DIR = FILESERVER_ROOT / "actuals"

PROJECTS_CSV = MASTERS_DIR / "projects.csv"
STAFF_CSV = MASTERS_DIR / "staff.csv"
PLANS_CSV = MASTERS_DIR / "plans.csv"


class SyncResult:
    def __init__(self):
        self.ok = True
        self.message = ""
        self.last_synced_at = None


def _read_csv_flexible(path: Path):
    """UTF-8(BOM可)優先、失敗時はCP932(Shift-JIS)でフォールバック"""
    for encoding in ("utf-8-sig", "cp932"):
        try:
            with open(path, "r", encoding=encoding, newline="") as f:
                return list(csv.DictReader(f))
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("csv", b"", 0, 1, f"{path} を UTF-8/CP932 のどちらでも読み込めませんでした")


def _write_csv(path: Path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with open(tmp_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    # 書き込み中の不完全ファイルを他クライアントが読まないよう、一時ファイル経由でアトミックに置き換える
    os.replace(tmp_path, path)


def is_fileserver_available() -> bool:
    try:
        return FILESERVER_ROOT.exists()
    except OSError:
        return False


# --- マスタ: ファイルサーバー → ローカルDB ---

def pull_masters() -> SyncResult:
    result = SyncResult()
    if not is_fileserver_available():
        result.ok = False
        result.message = "ファイルサーバーに接続できません。ローカルの内容で動作します。"
        return result

    try:
        if PROJECTS_CSV.exists():
            rows = _read_csv_flexible(PROJECTS_CSV)
            db.replace_all_projects(rows)

        if STAFF_CSV.exists():
            rows = _read_csv_flexible(STAFF_CSV)
            db.replace_all_staff(rows)

        if PLANS_CSV.exists():
            rows = _read_csv_flexible(PLANS_CSV)
            db.replace_all_plans(rows)

        result.last_synced_at = datetime.now()
        result.message = f"マスタを同期しました({result.last_synced_at:%H:%M:%S})"
    except Exception as e:
        result.ok = False
        result.message = f"マスタ同期中にエラーが発生しました: {e}"
    return result


# --- マスタ: ローカルDB → ファイルサーバー(管理者の保存操作時) ---

def push_projects() -> SyncResult:
    result = SyncResult()
    if not is_fileserver_available():
        result.ok = False
        result.message = "ファイルサーバーに接続できないため、ローカルにのみ保存しました。"
        return result
    try:
        rows = [dict(r) for r in db.list_projects()]
        _write_csv(PROJECTS_CSV, rows, fieldnames=["id", "name", "start_date", "end_date", "keywords", "status"])
        result.message = "案件マスタをファイルサーバーに反映しました"
    except Exception as e:
        result.ok = False
        result.message = f"案件マスタの書き戻しに失敗しました: {e}"
    return result


def push_staff() -> SyncResult:
    result = SyncResult()
    if not is_fileserver_available():
        result.ok = False
        result.message = "ファイルサーバーに接続できないため、ローカルにのみ保存しました。"
        return result
    try:
        rows = [dict(r) for r in db.list_staff()]
        _write_csv(STAFF_CSV, rows, fieldnames=["id", "name", "monthly_capacity_hours"])
        result.message = "要員マスタをファイルサーバーに反映しました"
    except Exception as e:
        result.ok = False
        result.message = f"要員マスタの書き戻しに失敗しました: {e}"
    return result


def push_plans(month: str) -> SyncResult:
    result = SyncResult()
    if not is_fileserver_available():
        result.ok = False
        result.message = "ファイルサーバーに接続できないため、ローカルにのみ保存しました。"
        return result
    try:
        # plans.csv は全月分をまとめて1ファイルに持つ想定。既存分を読み、対象月だけ入れ替える。
        existing = []
        if PLANS_CSV.exists():
            existing = _read_csv_flexible(PLANS_CSV)
        existing = [r for r in existing if r.get("month") != month]

        current_month_rows = [dict(r) for r in db.list_plans_for_month(month)]
        merged = existing + current_month_rows
        _write_csv(PLANS_CSV, merged, fieldnames=["id", "project_id", "staff_id", "month", "planned_hours"])
        result.message = f"{month}分の計画工数をファイルサーバーに反映しました"
    except Exception as e:
        result.ok = False
        result.message = f"計画工数の書き戻しに失敗しました: {e}"
    return result


# --- 実績: ローカルDB → 自分のファイル(1人1ファイル) ---

def push_my_actuals(staff_name: str) -> SyncResult:
    """自分の全実績を actuals/{氏名}.csv に書き出す(自分のファイルのみ書き込むので競合しない)"""
    result = SyncResult()
    if not is_fileserver_available():
        result.ok = False
        result.message = "ファイルサーバーに接続できないため、ローカルにのみ保存されています。次回接続時に同期してください。"
        return result
    try:
        rows = db.list_all_time_entries_for_staff_name(staff_name)
        path = ACTUALS_DIR / f"{staff_name}.csv"
        _write_csv(
            path,
            [dict(r) for r in rows],
            fieldnames=["id", "project_id", "staff_id", "start_time", "end_time", "source", "memo"],
        )
        result.last_synced_at = datetime.now()
        result.message = f"実績を同期しました({result.last_synced_at:%H:%M:%S})"
    except Exception as e:
        result.ok = False
        result.message = f"実績の同期に失敗しました: {e}"
    return result


# --- 実績: 全員分を読み込む(チーム集計・ダッシュボード用) ---

def pull_team_actuals():
    """actuals/*.csv を全部読み込んで一覧を返す(読み取り専用、他人のファイルは書き込まない)"""
    if not is_fileserver_available() or not ACTUALS_DIR.exists():
        return []
    all_rows = []
    for csv_file in ACTUALS_DIR.glob("*.csv"):
        try:
            rows = _read_csv_flexible(csv_file)
            all_rows.extend(rows)
        except Exception:
            # 1人分のファイルが読めなくても他の人の集計は継続する
            continue
    return all_rows
