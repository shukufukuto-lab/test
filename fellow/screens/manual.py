import flet as ft
from datetime import datetime, date
import db
import sync


def build_manual_view(page: ft.Page, staff_id: int):
    projects = db.list_projects()
    project_options = [ft.dropdown.Option(key=str(p["id"]), text=p["name"]) for p in projects]

    today_str = date.today().strftime("%Y-%m-%d")

    date_field = ft.TextField(label="日付 (YYYY-MM-DD)", value=today_str, width=180)
    project_dropdown = ft.Dropdown(label="案件", options=project_options, width=220)
    start_field = ft.TextField(label="開始 (HH:MM)", value="09:00", width=120)
    end_field = ft.TextField(label="終了 (HH:MM)", value="10:00", width=120)
    memo_field = ft.TextField(label="メモ(任意)", width=300)

    entries_list = ft.Column(spacing=4)

    def refresh_list():
        entries_list.controls.clear()
        entries = db.list_time_entries_for_date(staff_id, date_field.value)
        if not entries:
            entries_list.controls.append(ft.Text("入力済みの記録はありません", color=ft.Colors.GREY_500))
        for e in entries:
            start = datetime.fromisoformat(e["start_time"])
            end = datetime.fromisoformat(e["end_time"])
            hours = (end - start).total_seconds() / 3600
            entries_list.controls.append(
                ft.Row(
                    [
                        ft.Text(f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}", width=110),
                        ft.Text(e["project_name"], width=100),
                        ft.Text(f"{hours:.1f}h", width=60),
                        ft.Text(e["memo"] or "", color=ft.Colors.GREY_600, expand=True),
                        ft.Chip(label=ft.Text("タイマー" if e["source"] == "timer" else "手入力"), disabled=True),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_color=ft.Colors.RED_400,
                            on_click=lambda ev, eid=e["id"]: on_delete(eid),
                        ),
                    ]
                )
            )
        page.update()

    def on_delete(eid):
        db.delete_time_entry(eid)
        refresh_list()
        staff_name = db.get_staff_name(staff_id)
        if staff_name:
            sync.push_my_actuals(staff_name)

    def on_add(e):
        if not project_dropdown.value:
            page.open(ft.SnackBar(ft.Text("案件を選択してください")))
            return
        try:
            start_dt = datetime.strptime(f"{date_field.value} {start_field.value}", "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(f"{date_field.value} {end_field.value}", "%Y-%m-%d %H:%M")
        except ValueError:
            page.open(ft.SnackBar(ft.Text("日付・時刻の形式が正しくありません")))
            return
        if end_dt <= start_dt:
            page.open(ft.SnackBar(ft.Text("終了時刻は開始時刻より後にしてください")))
            return

        db.add_time_entry(
            int(project_dropdown.value),
            staff_id,
            start_dt.isoformat(timespec="seconds"),
            end_dt.isoformat(timespec="seconds"),
            source="manual",
            memo=memo_field.value,
        )
        memo_field.value = ""
        refresh_list()
        staff_name = db.get_staff_name(staff_id)
        if staff_name:
            sync.push_my_actuals(staff_name)

    add_button = ft.Button("追加", icon=ft.Icons.ADD, bgcolor=ft.Colors.INDIGO, color=ft.Colors.WHITE, on_click=on_add)
    date_field.on_change = lambda e: refresh_list()

    refresh_list()

    return ft.Column(
        [
            ft.Text("手動入力", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=12),
            ft.Card(
                content=ft.Container(
                    ft.Column(
                        [
                            ft.Row([date_field, project_dropdown, start_field, end_field]),
                            ft.Row([memo_field, add_button]),
                        ],
                        spacing=12,
                    ),
                    padding=20,
                )
            ),
            ft.Container(height=24),
            ft.Text("入力済み一覧", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(height=8),
            entries_list,
        ],
        scroll=ft.ScrollMode.AUTO,
    )
