import flet as ft
from datetime import datetime
import db
import sync

_timer_state = {"running": False, "start_time": None, "project_id": None, "seconds": 0}


def build_home_view(page: ft.Page, staff_id: int):
    projects = db.list_projects()
    project_options = [ft.dropdown.Option(key=str(p["id"]), text=p["name"]) for p in projects]

    project_dropdown = ft.Dropdown(
        label="案件を選択",
        options=project_options,
        value=str(_timer_state["project_id"]) if _timer_state["project_id"] else None,
        width=300,
    )

    timer_text = ft.Text("00:00:00", size=48, weight=ft.FontWeight.BOLD)
    status_text = ft.Text("停止中", color=ft.Colors.GREY_600)

    start_button = ft.Button("開始", icon=ft.Icons.PLAY_ARROW, bgcolor=ft.Colors.INDIGO, color=ft.Colors.WHITE)
    stop_button = ft.Button("停止", icon=ft.Icons.STOP, disabled=True)

    today_summary_column = ft.Column(spacing=6)

    def refresh_today_summary():
        today_summary_column.controls.clear()
        entries = db.list_time_entries_for_date(staff_id, datetime.now().strftime("%Y-%m-%d"))
        totals = {}
        for e in entries:
            start = datetime.fromisoformat(e["start_time"])
            end = datetime.fromisoformat(e["end_time"])
            hours = (end - start).total_seconds() / 3600
            totals[e["project_name"]] = totals.get(e["project_name"], 0) + hours

        if not totals:
            today_summary_column.controls.append(ft.Text("本日はまだ記録がありません", color=ft.Colors.GREY_500))
        else:
            max_h = max(totals.values()) or 1
            for name, hours in totals.items():
                today_summary_column.controls.append(
                    ft.Row(
                        [
                            ft.Text(name, width=100),
                            ft.Container(
                                ft.ProgressBar(value=min(hours / max(max_h, 4), 1), width=200, color=ft.Colors.INDIGO),
                            ),
                            ft.Text(f"{hours:.1f}h"),
                        ]
                    )
                )

    def tick():
        while _timer_state["running"]:
            elapsed = int((datetime.now() - _timer_state["start_time"]).total_seconds())
            h, rem = divmod(elapsed, 3600)
            m, s = divmod(rem, 60)
            timer_text.value = f"{h:02}:{m:02}:{s:02}"
            page.update()
            import time as _t
            _t.sleep(1)

    def on_start(e):
        if not project_dropdown.value:
            page.open(ft.SnackBar(ft.Text("案件を選択してください")))
            return
        _timer_state["running"] = True
        _timer_state["start_time"] = datetime.now()
        _timer_state["project_id"] = int(project_dropdown.value)
        status_text.value = f"計測中: {[p['name'] for p in projects if str(p['id']) == project_dropdown.value][0]}"
        status_text.color = ft.Colors.GREEN_700
        start_button.disabled = True
        stop_button.disabled = False
        project_dropdown.disabled = True
        page.update()
        page.run_thread(tick)

    def on_stop(e):
        _timer_state["running"] = False
        end_time = datetime.now()
        db.add_time_entry(
            _timer_state["project_id"],
            staff_id,
            _timer_state["start_time"].isoformat(timespec="seconds"),
            end_time.isoformat(timespec="seconds"),
            source="timer",
        )
        staff_name = db.get_staff_name(staff_id)
        if staff_name:
            sync.push_my_actuals(staff_name)
        status_text.value = "停止中"
        status_text.color = ft.Colors.GREY_600
        timer_text.value = "00:00:00"
        start_button.disabled = False
        stop_button.disabled = True
        project_dropdown.disabled = False
        page.update()
        refresh_today_summary()
        page.update()

    start_button.on_click = on_start
    stop_button.on_click = on_stop

    refresh_today_summary()

    return ft.Column(
        [
            ft.Text("ホーム", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=12),
            ft.Card(
                content=ft.Container(
                    ft.Column(
                        [
                            project_dropdown,
                            ft.Container(height=16),
                            ft.Row([timer_text], alignment=ft.MainAxisAlignment.CENTER),
                            ft.Row([status_text], alignment=ft.MainAxisAlignment.CENTER),
                            ft.Container(height=16),
                            ft.Row([start_button, stop_button], alignment=ft.MainAxisAlignment.CENTER, spacing=16),
                        ]
                    ),
                    padding=32,
                ),
            ),
            ft.Container(height=24),
            ft.Text("本日の実績", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(height=8),
            today_summary_column,
        ],
        scroll=ft.ScrollMode.AUTO,
    )
