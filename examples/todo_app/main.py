"""
KivyMD To-Do
============

A small but complete Material Design To-Do application built with KivyMD.

Features
--------
* Add, complete and delete tasks.
* Tasks are persisted to a JSON file between runs.
* Light / dark theme toggle from the top app bar.
* Empty-state hint when there are no tasks.
* A live counter of the remaining (active) tasks in the app bar.

Run it with::

    python examples/todo_app/main.py
"""

import json
import os

from kivy.lang import Builder
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout

from kivymd.app import MDApp
from kivymd.uix.list import TwoLineAvatarIconListItem
from kivymd.uix.snackbar import Snackbar

STORAGE_FILE = os.path.join(os.path.dirname(__file__), "tasks.json")

KV = """
<TaskRow>:
    IconLeftWidget:
        icon: root.check_icon
        theme_text_color: "Custom"
        text_color: app.theme_cls.primary_color if root.completed else app.theme_cls.disabled_hint_text_color
        on_release: root.toggle_completed()

    IconRightWidget:
        icon: "trash-can-outline"
        on_release: root.delete_task()


MDScreen:

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            id: toolbar
            title: "My Tasks"
            elevation: 4
            right_action_items:
                [["theme-light-dark", lambda x: app.toggle_theme(), "Toggle light / dark theme"]]

        MDBoxLayout:
            orientation: "horizontal"
            adaptive_height: True
            padding: "12dp", "8dp", "12dp", "8dp"
            spacing: "8dp"

            MDTextField:
                id: task_input
                hint_text: "What needs to be done?"
                mode: "rectangle"
                on_text_validate: app.add_task()

            MDIconButton:
                icon: "plus-circle"
                theme_text_color: "Custom"
                text_color: app.theme_cls.primary_color
                icon_size: "40sp"
                pos_hint: {"center_y": 0.5}
                on_release: app.add_task()

        MDBoxLayout:
            id: content
            orientation: "vertical"

            ScrollView:
                MDList:
                    id: task_list

    MDLabel:
        id: empty_label
        text: "No tasks yet.\\nAdd your first one above!"
        halign: "center"
        theme_text_color: "Hint"
        font_style: "H6"
"""


class TaskRow(TwoLineAvatarIconListItem):
    """A single to-do item rendered as a list row."""

    completed = BooleanProperty(False)
    check_icon = StringProperty("checkbox-blank-circle-outline")

    def __init__(self, app, task_id, **kwargs):
        self.app = app
        self.task_id = task_id
        super().__init__(**kwargs)
        self._sync_state()

    def toggle_completed(self):
        self.completed = not self.completed
        self._sync_state()
        self.app.on_task_changed()

    def delete_task(self):
        self.app.delete_task(self)

    def _sync_state(self):
        self.check_icon = (
            "check-circle"
            if self.completed
            else "checkbox-blank-circle-outline"
        )
        self.secondary_text = "Completed" if self.completed else "Active"


class TodoApp(MDApp):
    def build(self):
        self.title = "KivyMD To-Do"
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        self._next_id = 0
        return Builder.load_string(KV)

    def on_start(self):
        self._load_tasks()
        self._refresh_ui()

    # ----- task operations ------------------------------------------------
    def add_task(self):
        field = self.root.ids.task_input
        text = field.text.strip()
        if not text:
            Snackbar(text="Please type a task first.").open()
            return
        self._add_row(text, completed=False)
        field.text = ""
        self.on_task_changed()

    def delete_task(self, row):
        self.root.ids.task_list.remove_widget(row)
        self.on_task_changed()

    def toggle_theme(self):
        self.theme_cls.theme_style = (
            "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        )

    def on_task_changed(self):
        self._refresh_ui()
        self._save_tasks()

    # ----- helpers --------------------------------------------------------
    def _add_row(self, text, completed):
        self._next_id += 1
        row = TaskRow(app=self, task_id=self._next_id, text=text)
        row.completed = completed
        row._sync_state()
        self.root.ids.task_list.add_widget(row)

    def _iter_rows(self):
        return list(self.root.ids.task_list.children)[::-1]

    def _refresh_ui(self):
        rows = self._iter_rows()
        remaining = sum(1 for row in rows if not row.completed)
        self.root.ids.toolbar.title = (
            f"My Tasks ({remaining})" if rows else "My Tasks"
        )
        has_tasks = bool(rows)
        self.root.ids.content.opacity = 1 if has_tasks else 0
        self.root.ids.empty_label.opacity = 0 if has_tasks else 1

    # ----- persistence ----------------------------------------------------
    def _save_tasks(self):
        data = [
            {"text": row.text, "completed": row.completed}
            for row in self._iter_rows()
        ]
        try:
            with open(STORAGE_FILE, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
        except OSError as error:
            Snackbar(text=f"Could not save tasks: {error}").open()

    def _load_tasks(self):
        if not os.path.exists(STORAGE_FILE):
            return
        try:
            with open(STORAGE_FILE, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            return
        for item in data:
            self._add_row(item.get("text", ""), bool(item.get("completed")))


class _Root(BoxLayout):
    """Kept for factory registration compatibility; unused directly."""


if __name__ == "__main__":
    TodoApp().run()
