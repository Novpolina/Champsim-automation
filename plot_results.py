import json
import matplotlib.pyplot as plt

def main():
    
    with open('l2_hit_rates.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    x_configs = sorted(list({(d['size_kb'], d['sets'], d['ways']) for d in data}))
    x_labels = [f"{size}KB\n({sets}s/{ways}w)" for size, sets, ways in x_configs]

    policies = {
        'lru_no_prefetch': {'label': 'LRU (Без префетчера)', 'color': '#e74c3c', 'marker': 'o', 'y': []},
        'ship_no_prefetch': {'label': 'SHIP (Без префетчера)', 'color': '#3498db', 'marker': 's', 'y': []},
        'ship_spp_dev': {'label': 'SHIP + SPP', 'color': '#2ecc71', 'marker': '^', 'y': []}
    }

    for policy in policies:
        policy_data = [d for d in data if d['policy'] == policy]
        if not policy_data:
            continue
            
        policy_data.sort(key=lambda x: (x['size_kb'], x['sets'], x['ways']))
        policies[policy]['y'] = [d['geomean'] for d in policy_data]

    plt.figure(figsize=(10, 6))

    for policy, props in policies.items():
        if props['y']:
            plt.plot(x_labels, props['y'], label=props['label'], color=props['color'], marker=props['marker'], linewidth=2, markersize=8)

    plt.title('Зависимость L2 Hit Rate от размера кэша и политики', fontsize=14, pad=15)
    plt.xlabel('Размер кэша (и конфигурация Sets/Ways)', fontsize=12)
    plt.ylabel('Geomean L2 Hit Rate', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=11)
    plt.tight_layout()

    output_image = 'l2_hit_rate_chart.png'
    plt.savefig(output_image, dpi=300)

if __name__ == "__main__":
    main()