from backend.services.risk_service import calculate_risk

def test_risk_benign_low_confidence():
    score, level = calculate_risk('Benign', 0.5, False)
    assert level == 'LOW'

def test_risk_ddos_high_confidence():
    score, level = calculate_risk('DDoS', 0.95, False)
    assert level == 'HIGH'
    
def test_risk_anomaly_boost():
    score1, level1 = calculate_risk('Benign', 0.9, False)
    score2, level2 = calculate_risk('Benign', 0.9, True)
    assert score2 > score1
