import flet as ft
from datetime import date
import db
import sync


def build_dashboard_view(page: ft.Page, staff_id: int):
    month_field = ft.TextField(label="対象月 (YYYY-MM)", value=date.today().strftime("%Y-%m"), width=160)
    scope_dropdown = ft.Dropdown(
        label="表示",
        width=140,
        value="自分",
        options=[ft.dropdown.Option("自分"), ft.dropdown.Option("チーム")],
    )
    result_column = ft.Column(spacing=10)

    def refresh():
        result_column.controls.clear()
        month = month_field.value
        projects = db.list_projects()
        plans = db.list_plans_for_month(month)

        planned_by_project = {}
        for row in plans:
            planned_by_project[row["project_id"]] = planned_by_project.get(row["project_id"], 0) + row["planned_hours"]

        if scope_dropdown.value == "チーム":
            team_rows = sync.pull_team_actuals()
            if team_rows:
                actual_by_project = db.sum_actual_hours_from_rows(team_rows, month)
            else:
                # ファイルサーバーに接続できない場合は、自分のローカルDBの分だけで代替表示する
                actual_by_project = {
                    row["project_id"]: row["actual_hours"] for row in db.sum_actual_hours_for_month(month)
                }
        else:
            actual_by_project = {
                row["project_id"]: row["actual_hours"]
                for row in db.sum_actual_hours_for_month(month)
                if row["staff_id"] == staff_id
            }

        if not projects:
            result_column.controls.append(ft.Text("案件が登録されていません", color=ft.Colors.GREY_500))

        for p in projects:
            planned = planned_by_project.get(p["id"], 0)
            actual = actual_by_project.get(p["id"], 0)
            rate = (actual / planned * 100) if planned > 0 else 0
            over = rate > 100

            bar_color = ft.Colors.RED_400 if over else ft.Colors.INDIGO
            warning = ft.Row(
                [ft.Icon(ft.Icons.WARNING_AMBER, color=ft.Colors.RED_400, size=16), ft.Text("計画超過", color=ft.Colors.RED_400, size=12)]
            ) if over else ft.Container()

            result_column.controls.append(
                ft.Card(
                    content=ft.Container(
                        ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text(p["name"], size=16, weight=ft.FontWeight.BOLD),
                                        ft.Container(expand=True),
                                        warning,
                                    ]
                                ),
                                ft.Row(
                                    [
                                        ft.Text(f"計画 {planned:.0f}h"),
                                        ft.Text("→"),
                                        ft.Text(f"実績 {actual:.1f}h"),
                                        ft.Text(f"({rate:.0f}%)", color=bar_color, weight=ft.FontWeight.BOLD),
                                    ],
                                    spacing=8,
                                ),
                                ft.ProgressBar(value=min(rate / 100, 1), color=bar_color),
                            ],
                            spacing=6,
                        ),
                        padding=16,
                    )
                )
            )
        page.update()

    month_field.on_change = lambda e: refresh()
    scope_dropdown.on_change = lambda e: refresh()
    refresh()

    return ft.Column(
        [
            ft.Text("集計・ダッシュボード", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=12),
            ft.Row([month_field, scope_dropdown]),
            ft.Container(height=16),
            ft.Text("案件別 計画 vs 実績", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(height=8),
            result_column,
        ],
        scroll=ft.ScrollMode.AUTO,
    )
