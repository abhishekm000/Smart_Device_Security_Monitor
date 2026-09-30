def calculate_risk(prediction, confidence, is_anomaly):
    """
    Risk scoring engine.
    Returns: risk_score (0-100), risk_level (LOW, MEDIUM, HIGH)
    """
    base_score = 0
    
    if prediction == 'Benign':
        base_score = 10
    elif prediction in ['Reconnaissance', 'Spoofing']:
        base_score = 60
    elif prediction in ['DoS', 'DDoS', 'Brute Force', 'Mirai', 'Web-based attacks']:
        base_score = 85
    else:
        base_score = 50

    # Adjust based on confidence
    if prediction != 'Benign':
        risk_score = base_score + (confidence * 10)
    else:
        risk_score = base_score - (confidence * 5)
        
    # Adjust based on anomaly
    if is_anomaly and prediction == 'Benign':
        risk_score += 30 # Suspicious unknown behavior
    elif is_anomaly:
        risk_score += 5
        
    risk_score = max(0, min(100, int(risk_score)))
    
    if risk_score < 30:
        risk_level = "LOW"
    elif risk_score < 70:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"
        
    return risk_score, risk_level
