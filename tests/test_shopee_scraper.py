import pytest
from unittest.mock import Mock
from scraper.shopee_scraper import ShopeeScraper, human_pause, human_scroll


class TestHumanHelpers:
    """Testes para funções auxiliares de comportamento humano."""
    
    def test_human_pause_runs_without_error(self):
        """Verifica que human_pause executa sem erros."""
        human_pause(0.01, 0.02)
    
    def test_human_scroll_with_distance(self):
        """Verifica que human_scroll executa com distância especificada."""
        mock_page = Mock()
        mock_page.mouse.wheel = Mock()
        
        human_scroll(mock_page, distance=100)
        
        assert mock_page.mouse.wheel.call_count >= 1


class TestShopeeScraper:
    """Testes para a classe ShopeeScraper."""
    
    def test_scraper_initialization_default(self):
        """Verifica inicialização padrão do scraper."""
        scraper = ShopeeScraper()
        
        assert scraper.storage_state_path is None
        assert scraper.proxy is None
    
    def test_close_overlay_if_present_no_overlay(self):
        """Verifica comportamento quando não há overlay."""
        scraper = ShopeeScraper()
        mock_page = Mock()
        mock_page.query_selector = Mock(return_value=None)
        
        result = scraper._close_overlay_if_present(mock_page)
        
        assert result is False
    
    def test_close_overlay_if_present_with_overlay(self):
        """Verifica comportamento quando há overlay presente."""
        scraper = ShopeeScraper()
        mock_page = Mock()
        
        mock_element = Mock()
        mock_element.bounding_box = Mock(return_value={"x": 100, "y": 100, "width": 50, "height": 50})
        mock_element.click = Mock()
        
        mock_page.query_selector = Mock(return_value=mock_element)
        mock_page.mouse.move = Mock()
        
        result = scraper._close_overlay_if_present(mock_page)
        
        assert result is True
