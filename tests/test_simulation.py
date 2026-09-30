from backend.services.simulation_service import SimulationService
from unittest.mock import patch

def test_simulation_start_stop():
    service = SimulationService()
    
    # Mock load_dataset to return True without actually loading a huge CSV if it takes long
    with patch.object(service, 'load_dataset', return_value=True):
        service.dataset = [1, 2, 3] # mock dataset length
        
        success, msg = service.start()
        assert success is True
        assert service.is_running is True
        
        success, msg = service.stop()
        assert success is True
        assert service.is_running is False
