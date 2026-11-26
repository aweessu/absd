"""Проверки оболочки и интеграции. Не содержат решений учебной аналитики."""

from pathlib import Path
import unittest
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest

from ui.integration import call_user_loader

ROOT = Path(__file__).resolve().parents[1]


class InterfaceTests(unittest.TestCase):
    def app(self):
        return AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()

    def assert_clean(self, app):
        self.assertEqual(len(app.exception), 0, [item.message for item in app.exception])

    def test_all_pages_and_demo_slices(self):
        app = self.app()
        self.assert_clean(app)
        for scenario in ("global", "us", "europe", "remote"):
            app.selectbox(key="scenario").set_value(scenario).run()
            for page in ("Обзор рынка", "Специализации", "Формат работы", "Динамика зарплат", "Мои данные", "Мастерская"):
                app.radio(key="page").set_value(page).run()
                self.assert_clean(app)

    def test_metric_toggle_and_reset(self):
        app = self.app()
        app.selectbox(key="scenario").set_value("us").run()
        before = app.get("plotly_chart")[0].proto.spec
        app.radio(key="salary_metric").set_value("Медиана").run()
        after = app.get("plotly_chart")[0].proto.spec
        self.assertNotEqual(before, after)
        app.button(key="reset_demo").click().run()
        self.assertEqual(app.selectbox(key="scenario").value, "global")
        self.assertEqual(app.radio(key="salary_metric").value, "Средняя")
        self.assert_clean(app)

    def test_table_search_and_empty_state(self):
        app = self.app()
        app.radio(key="page").set_value("Мои данные").run()
        app.radio(key="data_mode").set_value("Демопример").run()
        app.text_input(key="sample_query").set_value("ML Engineer").run()
        self.assertEqual(len(app.dataframe[0].value), 1)
        app.multiselect(key="sample_levels").set_value(["EN"]).run()
        self.assertEqual(len(app.dataframe), 0)
        self.assertTrue(any("нет совпадений" in item.value for item in app.info))
        self.assert_clean(app)

    def test_unfinished_task_gives_hint(self):
        app = self.app()
        app.radio(key="page").set_value("Мои данные").run()
        with patch("ui.views.call_user_loader", side_effect=NotImplementedError()):
            app.button(key="load_user").click().run()
        self.assertTrue(any("Сначала реализуй" in item.value for item in app.warning))
        self.assertFalse(app.session_state["lesson_1_complete"])
        self.assert_clean(app)

    def test_success_is_visible_and_error_clears_stale_result(self):
        app = self.app()
        app.radio(key="page").set_value("Мои данные").run()
        example = pd.DataFrame({"interface_test": ["returned value"]})
        with patch("ui.views.call_user_loader", return_value=example):
            app.button(key="load_user").click().run()
        self.assertTrue(app.session_state["lesson_1_complete"])
        self.assertEqual(app.dataframe[0].value.iloc[0,0], "returned value")
        with patch("ui.views.call_user_loader", side_effect=FileNotFoundError()):
            app.button(key="load_user").click().run()
        self.assertFalse(app.session_state["lesson_1_complete"])
        self.assertEqual(len(app.dataframe), 0)
        self.assertTrue(any("Файл не найден" in item.value for item in app.warning))
        self.assert_clean(app)

    def test_workshop_navigation(self):
        app = self.app()
        app.button(key="open_workshop").click().run()
        self.assertEqual(app.radio(key="page").value, "Мастерская")
        app.button(key="task_open_data").click().run()
        self.assertEqual(app.radio(key="page").value, "Мои данные")
        self.assert_clean(app)


class IntegrationContractTests(unittest.TestCase):
    def test_rejects_non_dataframe(self):
        with patch("ui.integration.runpy.run_path", return_value={"load_dataset": lambda path: None}):
            with self.assertRaisesRegex(TypeError, "return"):
                call_user_loader("data/example.txt")

    def test_rejects_empty_dataframe(self):
        with patch("ui.integration.runpy.run_path", return_value={"load_dataset": lambda path: pd.DataFrame()}):
            with self.assertRaisesRegex(ValueError, "пустой"):
                call_user_loader("data/example.txt")

    def test_passes_resolved_path_and_preserves_dataframe(self):
        example = pd.DataFrame({"interface_test": [1]})
        with patch("ui.integration.runpy.run_path", return_value={"load_dataset": lambda path: example}) as runner:
            self.assertIs(call_user_loader("data/example.txt"), example)
            runner.assert_called_once_with(str(ROOT / "analysis" / "loader.py"))


if __name__ == "__main__":
    unittest.main()
