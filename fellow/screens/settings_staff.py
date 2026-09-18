import flet as ft
import db
import sync


def build_staff_view(page: ft.Page, staff_id: int):
    name_field = ft.TextField(label="氏名", width=200)
    capacity_field = ft.TextField(label="月間稼働可能時間", width=180, value="160")

    table_column = ft.Column(spacing=4)

    def refresh():
        table_column.controls.clear()
        table_column.controls.append(
            ft.Row(
                [
                    ft.Text("氏名", width=150, weight=ft.FontWeight.BOLD),
                    ft.Text("月間稼働可能時間", width=180, weight=ft.FontWeight.BOLD),
                    ft.Text("", width=40),
                ]
            )
        )
        for s in db.list_staff():
            table_column.controls.append(
                ft.Row(
                    [
                        ft.Text(s["name"], width=150),
                        ft.Text(f"{s['monthly_capacity_hours']:.0f}h", width=180),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_color=ft.Colors.RED_400,
                            on_click=lambda e, sid=s["id"]: on_delete(sid),
                        ),
                    ]
                )
            )
        page.update()

    def on_delete(sid):
        db.delete_staff(sid)
        refresh()
        sync.push_staff()

    def on_add(e):
        if not name_field.value:
            page.open(ft.SnackBar(ft.Text("氏名を入力してください")))
            return
        try:
            capacity = float(capacity_field.value)
        except ValueError:
            page.open(ft.SnackBar(ft.Text("稼働可能時間は数値で入力してください")))
            return
        db.add_staff(name_field.value, capacity)
        name_field.value = ""
        capacity_field.value = "160"
        refresh()
        result = sync.push_staff()
        page.open(ft.SnackBar(ft.Text(result.message)))
        page.update()

    add_button = ft.Button("要員を追加", icon=ft.Icons.ADD, bgcolor=ft.Colors.INDIGO, color=ft.Colors.WHITE, on_click=on_add)

    refresh()

    return ft.Column(
        [
            ft.Text("要員マスタ", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=12),
            ft.Card(
                content=ft.Container(
                    ft.Row([name_field, capacity_field, add_button]),
                    padding=20,
                )
            ),
            ft.Container(height=24),
            ft.Text("要員一覧", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(height=8),
            table_column,
        ],
        scroll=ft.ScrollMode.AUTO,
    )
