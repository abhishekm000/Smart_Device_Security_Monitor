import csv
import random
import os

def generate_synthetic_ciciot2023(num_samples=1000, output_path='data/sample/ciciot2023_sample.csv'):
    random.seed(42)
    
    columns = [
        'flow_duration', 'Header_Length', 'Protocol Type', 'Duration',
        'Rate', 'Srate', 'Drate', 'fin_flag_number', 'syn_flag_number',
        'rst_flag_number', 'psh_flag_number', 'ack_flag_number',
        'ece_flag_number', 'cwr_flag_number', 'ack_count',
        'syn_count', 'fin_count', 'urg_count', 'rst_count',
        'HTTP', 'HTTPS', 'DNS', 'Telnet', 'SMTP', 'SSH', 'IRC', 'TCP',
        'UDP', 'DHCP', 'ARP', 'ICMP', 'IPv', 'LLC', 'Tot sum', 'Min',
        'Max', 'AVG', 'Std', 'Tot size', 'IAT', 'Number', 'Magnitue',
        'Radius', 'Covariance', 'Variance', 'Weight', 'label'
    ]
    
    classes = ['Benign', 'DDoS', 'DoS', 'Mirai', 'Reconnaissance', 'Spoofing', 'Brute Force', 'Web-based attacks']
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        
        for _ in range(num_samples):
            label = random.choice(classes)
            is_attack = label != 'Benign'
            rate_multiplier = 10 if is_attack and label in ['DDoS', 'DoS', 'Mirai'] else 1
            
            row = [
                random.uniform(0.1, 100.0) if not is_attack else random.uniform(0.01, 10.0), # flow_duration
                random.randint(14, 1500), # Header_Length
                float(random.choice([6, 17, 1])), # Protocol Type
                random.uniform(0.1, 64.0), # Duration
                random.uniform(10, 100) * rate_multiplier, # Rate
                random.uniform(10, 100) * rate_multiplier, # Srate
                random.uniform(0, 50), # Drate
                float(random.choices([0, 1], weights=[0.9, 0.1])[0]), # fin_flag_number
                float(random.choices([0, 1], weights=[0.9, 0.1])[0]), # syn_flag_number
                float(random.choices([0, 1], weights=[0.95, 0.05])[0]), # rst_flag_number
                float(random.choices([0, 1], weights=[0.8, 0.2])[0]), # psh_flag_number
                float(random.choices([0, 1], weights=[0.5, 0.5])[0]), # ack_flag_number
                0.0, # ece_flag_number
                0.0, # cwr_flag_number
                random.uniform(0, 100), # ack_count
                random.uniform(0, 10) * (5 if label == 'DoS' else 1), # syn_count
                random.uniform(0, 5), # fin_count
                random.uniform(0, 2), # urg_count
                random.uniform(0, 5), # rst_count
                float(random.choices([0, 1], weights=[0.8, 0.2])[0]), # HTTP
                float(random.choices([0, 1], weights=[0.7, 0.3])[0]), # HTTPS
                float(random.choices([0, 1], weights=[0.9, 0.1])[0]), # DNS
                float(random.choices([0, 1], weights=[0.99, 0.01])[0]), # Telnet
                float(random.choices([0, 1], weights=[0.99, 0.01])[0]), # SMTP
                float(random.choices([0, 1], weights=[0.95, 0.05])[0]), # SSH
                0.0, # IRC
                float(random.choices([0, 1], weights=[0.5, 0.5])[0]), # TCP
                float(random.choices([0, 1], weights=[0.5, 0.5])[0]), # UDP
                float(random.choices([0, 1], weights=[0.98, 0.02])[0]), # DHCP
                float(random.choices([0, 1], weights=[0.95, 0.05])[0]), # ARP
                float(random.choices([0, 1], weights=[0.9, 0.1])[0]), # ICMP
                float(random.choices([0, 1], weights=[0.1, 0.9])[0]), # IPv
                float(random.choices([0, 1], weights=[0.1, 0.9])[0]), # LLC
                random.uniform(100, 10000), # Tot sum
                random.uniform(0, 100), # Min
                random.uniform(100, 1500), # Max
                random.uniform(50, 800), # AVG
                random.uniform(10, 300), # Std
                random.uniform(50, 1500), # Tot size
                random.uniform(0.001, 1.0) / rate_multiplier, # IAT
                random.uniform(1, 100), # Number
                random.uniform(10, 100), # Magnitue
                random.uniform(10, 100), # Radius
                random.uniform(0, 1000), # Covariance
                random.uniform(0, 1000), # Variance
                random.uniform(0.1, 10.0), # Weight
                label # label
            ]
            writer.writerow(row)
            
    print(f"Generated synthetic dataset with {num_samples} rows at {output_path}")

if __name__ == '__main__':
    generate_synthetic_ciciot2023()
