from ml.preprocessing import normalize_label

def test_normalize_label_benign():
    assert normalize_label('Benign_Traffic') == 'Benign'

def test_normalize_label_ddos():
    assert normalize_label('DDoS-UDP_Flood') == 'DDoS'
    
def test_normalize_label_brute():
    assert normalize_label('BruteForce-Web') == 'Brute Force'
