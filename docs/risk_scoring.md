# Risk Scoring Engine

The risk score is a composite metric from 0 to 100 that determines how an alert is prioritized on the SOC dashboard.

## Formula
1. **Base Score**: Assigned based on the attack category.
   - Benign: 10
   - Reconnaissance / Spoofing: 60
   - DoS / DDoS / Mirai: 85
2. **Confidence Modifier**: 
   - If Attack: `+ (Confidence * 10)` (Higher confidence = higher risk)
   - If Benign: `- (Confidence * 5)` (Higher confidence = lower risk)
3. **Anomaly Modifier**:
   - If flagged as Anomaly & Predicted Benign: `+ 30` (Suspicious unknown behavior)
   - If flagged as Anomaly & Predicted Attack: `+ 5`

## Thresholds
- **LOW**: 0 - 29
- **MEDIUM**: 30 - 69
- **HIGH**: 70 - 100
