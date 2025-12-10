import sys
import types
import pytest
from unittest.mock import Mock

# If Playwright is not installed in the test environment, provide a minimal stub
# so importing `scraper.ml_scraper` does not raise ModuleNotFoundError.
if 'playwright.sync_api' not in sys.modules:
    sync_api_mod = types.ModuleType('playwright.sync_api')
    def sync_playwright_stub():
        class Ctx:
            def __enter__(self):
                return Mock()
            def __exit__(self, exc_type, exc, tb):
                return False
        return Ctx()
    sync_api_mod.sync_playwright = sync_playwright_stub
    sys.modules['playwright'] = types.ModuleType('playwright')
    sys.modules['playwright.sync_api'] = sync_api_mod

from scraper.ml_scraper import MLScraper, human_pause, human_scroll


class TestHumanHelpers:
    """Testes para funções helper de comportamento humano."""

    def test_human_pause_runs_without_error(self):
        """Verifica que human_pause executa sem erros."""
        human_pause(0.001, 0.002)

    def test_human_scroll_with_small_distance(self):
        """Verifica que human_scroll lida com distâncias pequenas."""
        mock_page = Mock()
        mock_page.mouse = Mock()
        mock_page.mouse.wheel = Mock()

        human_scroll(mock_page, distance=10)

        assert mock_page.mouse.wheel.call_count >= 1

    def test_human_scroll_with_large_distance(self):
        """Verifica que human_scroll lida com distâncias grandes."""
        mock_page = Mock()
        mock_page.mouse = Mock()
        mock_page.mouse.wheel = Mock()

        human_scroll(mock_page, distance=500)

        assert mock_page.mouse.wheel.call_count >= 2


class TestMLScraper:
    """Testes para a classe MLScraper"""

    def test_scraper_initialization_default(self):
        scraper = MLScraper()
        assert scraper is not None

    def test_close_overlay_if_present_no_overlay(self):
        scraper = MLScraper()
        mock_page = Mock()
        mock_page.query_selector = Mock(return_value=None)

        result = scraper._close_overlay_if_present(mock_page)

        assert result is False
        assert mock_page.query_selector.called

    def test_close_overlay_if_present_with_overlay(self):
        scraper = MLScraper()
        mock_page = Mock()

        mock_element = Mock()
        mock_element.bounding_box = Mock(return_value={"x": 100, 
                                                       "y": 100, 
                                                       "width": 50, 
                                                       "height": 50})
        mock_element.click = Mock()

        mock_page.query_selector = Mock(return_value=mock_element)
        mock_page.mouse = Mock()
        mock_page.mouse.move = Mock()

        result = scraper._close_overlay_if_present(mock_page)

        assert result is True
        assert mock_element.click.called

    def test_click_banner_if_present_no_banner(self):
        scraper = MLScraper()
        mock_page = Mock()
        mock_page.query_selector = Mock(return_value=None)

        result = scraper._click_banner_if_present(mock_page)

        assert result is False

    def test_click_banner_if_present_with_banner(self):
        scraper = MLScraper()
        mock_page = Mock()

        mock_element = Mock()
        mock_element.is_visible = Mock(return_value=True)
        mock_element.bounding_box = Mock(return_value={"x": 10, 
                                                       "y": 10, 
                                                       "width": 20, 
                                                       "height": 20})
        mock_element.click = Mock()

        mock_page.query_selector = Mock(return_value=mock_element)
        mock_page.mouse = Mock()
        mock_page.mouse.move = Mock()

        result = scraper._click_banner_if_present(mock_page)

        assert result is True
        assert mock_element.click.called


@pytest.mark.skip(reason="Teste de integração")
def test_scrape_produto_integration():
    """Teste de integração (abre navegador)."""
    scraper = MLScraper()
    scraper.scrape_produto()

    import os
    assert os.path.exists("produtos.csv")

