import flet as ft
from datetime import datetime, timedelta

import db
from screens.home import build_home_view
from screens.manual import build_manual_view
from screens.dashboard import build_dashboard_view
from screens.settings_projects import build_projects_view
from screens.settings_staff import build_staff_view
from screens.settings_plans import build_plans_view

CURRENT_STAFF_ID = 1  # プロトタイプでは固定。将来はログインユーザーに応じて切替


def main(page: ft.Page):
    page.title = "Fellow - 工数管理"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.INDIGO)
    page.window.width = 1000
    page.window.height = 720
    page.padding = 0

    db.init_db()

    content_area = ft.Container(expand=True, padding=24)

    def show(view_builder):
        content_area.content = view_builder(page, CURRENT_STAFF_ID)
        page.update()

    def on_nav_change(e: ft.ControlEvent):
        idx = e.control.selected_index
        views = {
            0: build_home_view,
            1: build_manual_view,
            2: build_dashboard_view,
            3: build_projects_view,
            4: build_staff_view,
            5: build_plans_view,
        }
        show(views[idx])

    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        bgcolor=ft.Colors.SURFACE,
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.TIMER_OUTLINED, selected_icon=ft.Icons.TIMER, label="ホーム"),
            ft.NavigationRailDestination(icon=ft.Icons.EDIT_NOTE_OUTLINED, selected_icon=ft.Icons.EDIT_NOTE, label="手動入力"),
            ft.NavigationRailDestination(icon=ft.Icons.BAR_CHART_OUTLINED, selected_icon=ft.Icons.BAR_CHART, label="集計"),
            ft.NavigationRailDestination(icon=ft.Icons.FOLDER_OUTLINED, selected_icon=ft.Icons.FOLDER, label="案件"),
            ft.NavigationRailDestination(icon=ft.Icons.PEOPLE_OUTLINE, selected_icon=ft.Icons.PEOPLE, label="要員"),
            ft.NavigationRailDestination(icon=ft.Icons.CALENDAR_MONTH_OUTLINED, selected_icon=ft.Icons.CALENDAR_MONTH, label="計画工数"),
        ],
        on_change=on_nav_change,
    )

    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                content_area,
            ],
            expand=True,
        )
    )

    show(build_home_view)


if __name__ == "__main__":
    ft.run(main)
