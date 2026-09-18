import flet as ft
import db
import sync


def build_projects_view(page: ft.Page, staff_id: int):
    name_field = ft.TextField(label="案件名", width=200)
    start_field = ft.TextField(label="開始日 (YYYY-MM-DD)", width=160)
    end_field = ft.TextField(label="終了日 (YYYY-MM-DD)", width=160)
    keywords_field = ft.TextField(label="自動検知キーワード(カンマ区切り)", width=280)
    status_dropdown = ft.Dropdown(
        label="状態",
        width=140,
        value="進行中",
        options=[ft.dropdown.Option(s) for s in ["未開始", "進行中", "完了"]],
    )

    table_column = ft.Column(spacing=4)

    def refresh():
        table_column.controls.clear()
        table_column.controls.append(
            ft.Row(
                [
                    ft.Text("案件名", width=150, weight=ft.FontWeight.BOLD),
                    ft.Text("期間", width=200, weight=ft.FontWeight.BOLD),
                    ft.Text("状態", width=80, weight=ft.FontWeight.BOLD),
                    ft.Text("キーワード", width=200, weight=ft.FontWeight.BOLD),
                    ft.Text("", width=40),
                ]
            )
        )
        for p in db.list_projects():
            table_column.controls.append(
                ft.Row(
                    [
                        ft.Text(p["name"], width=150),
                        ft.Text(f"{p['start_date'] or ''} ~ {p['end_date'] or ''}", width=200),
                        ft.Text(p["status"], width=80),
                        ft.Text(p["keywords"] or "", width=200, color=ft.Colors.GREY_600),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_color=ft.Colors.RED_400,
                            on_click=lambda e, pid=p["id"]: on_delete(pid),
                        ),
                    ]
                )
            )
        page.update()

    def on_delete(pid):
        db.delete_project(pid)
        refresh()
        sync.push_projects()

    def on_add(e):
        if not name_field.value:
            page.open(ft.SnackBar(ft.Text("案件名を入力してください")))
            return
        db.add_project(
            name_field.value,
            start_field.value,
            end_field.value,
            keywords_field.value,
            status_dropdown.value,
        )
        name_field.value = ""
        start_field.value = ""
        end_field.value = ""
        keywords_field.value = ""
        refresh()
        result = sync.push_projects()
        page.open(ft.SnackBar(ft.Text(result.message)))
        page.update()

    add_button = ft.Button("案件を追加", icon=ft.Icons.ADD, bgcolor=ft.Colors.INDIGO, color=ft.Colors.WHITE, on_click=on_add)

    refresh()

    return ft.Column(
        [
            ft.Text("案件マスタ", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=12),
            ft.Card(
                content=ft.Container(
                    ft.Column(
                        [
                            ft.Row([name_field, start_field, end_field, status_dropdown]),
                            ft.Row([keywords_field, add_button]),
                        ],
                        spacing=12,
                    ),
                    padding=20,
                )
            ),
            ft.Container(height=24),
            ft.Text("案件一覧", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(height=8),
            table_column,
        ],
        scroll=ft.ScrollMode.AUTO,
    )
