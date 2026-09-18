import flet as ft
from datetime import date
import db
import sync


def build_plans_view(page: ft.Page, staff_id: int):
    projects = db.list_projects()
    staff_members = db.list_staff()

    month_field = ft.TextField(label="対象月 (YYYY-MM)", value=date.today().strftime("%Y-%m"), width=160)

    matrix_column = ft.Column(spacing=4)
    field_refs = {}

    def build_matrix():
        matrix_column.controls.clear()
        field_refs.clear()
        month = month_field.value

        header = [ft.Text("要員", width=100, weight=ft.FontWeight.BOLD)]
        for p in projects:
            header.append(ft.Text(p["name"], width=110, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER))
        matrix_column.controls.append(ft.Row(header))

        existing = {(row["project_id"], row["staff_id"]): row["planned_hours"] for row in db.list_plans_for_month(month)}

        for s in staff_members:
            row_controls = [ft.Text(s["name"], width=100)]
            for p in projects:
                current = existing.get((p["id"], s["id"]), 0)
                tf = ft.TextField(value=str(current), width=90, text_align=ft.TextAlign.RIGHT, dense=True)
                field_refs[(p["id"], s["id"])] = tf
                row_controls.append(tf)
            matrix_column.controls.append(ft.Row(row_controls))

        totals_row = [ft.Text("月合計", width=100, weight=ft.FontWeight.BOLD)]
        for p in projects:
            total = sum(existing.get((p["id"], s["id"]), 0) for s in staff_members)
            totals_row.append(ft.Text(f"{total:.0f}h", width=110, text_align=ft.TextAlign.CENTER))
        matrix_column.controls.append(ft.Divider())
        matrix_column.controls.append(ft.Row(totals_row))
        page.update()

    def on_save(e):
        month = month_field.value
        for (project_id, sid), tf in field_refs.items():
            try:
                hours = float(tf.value or 0)
            except ValueError:
                hours = 0
            db.set_plan(project_id, sid, month, hours)
        result = sync.push_plans(month)
        page.open(ft.SnackBar(ft.Text(result.message)))
        build_matrix()

    month_field.on_change = lambda e: build_matrix()
    save_button = ft.Button("保存", icon=ft.Icons.SAVE, bgcolor=ft.Colors.INDIGO, color=ft.Colors.WHITE, on_click=on_save)

    build_matrix()

    return ft.Column(
        [
            ft.Text("計画工数登録", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=12),
            ft.Row([month_field, save_button]),
            ft.Container(height=16),
            ft.Card(content=ft.Container(matrix_column, padding=20)),
        ],
        scroll=ft.ScrollMode.AUTO,
    )
