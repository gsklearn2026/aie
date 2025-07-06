import pytest
from app.services.provider_manager import ProviderManager
from app.providers.mock_provider import MockProvider

@pytest.mark.asyncio
async def test_provider_manager_add_providers():
    manager = ProviderManager()
    mock1 = MockProvider("mock1")
    mock2 = MockProvider("mock2")
    
    manager.add_provider(mock1, True)
    manager.add_provider(mock2)
    
    providers = manager.get_provider_names()
    assert "mock1" in providers
    assert "mock2" in providers

@pytest.mark.asyncio
async def test_primary_provider_usage():
    manager = ProviderManager()
    mock1 = MockProvider("mock1")
    mock2 = MockProvider("mock2")
    
    manager.add_provider(mock1, True)
    manager.add_provider(mock2)
    
    response = await manager.generate_text("test prompt")
    assert response["provider"] == "mock1"

@pytest.mark.asyncio
async def test_failover_mechanism():
    manager = ProviderManager()
    mock1 = MockProvider("mock1", should_fail=True)
    mock2 = MockProvider("mock2")
    
    manager.add_provider(mock1, True)
    manager.add_provider(mock2)
    
    response = await manager.generate_text("test prompt")
    assert response["provider"] == "mock2"

@pytest.mark.asyncio
async def test_all_providers_fail():
    manager = ProviderManager()
    mock1 = MockProvider("mock1", should_fail=True)
    mock2 = MockProvider("mock2", should_fail=True)
    
    manager.add_provider(mock1, True)
    manager.add_provider(mock2)
    
    with pytest.raises(Exception) as excinfo:
        await manager.generate_text("test prompt")
    
    assert "All providers failed" in str(excinfo.value)
