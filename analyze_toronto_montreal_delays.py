import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the data
df = pd.read_csv('via_data_filtered.csv')

# Filter for Toronto to Montreal trains only
toronto_montreal = df[(df['from'] == 'TORONTO') & (df['to'] == 'MONTRÉAL')].copy()

# Get unique train instances (train_id + instance combination)
train_instances = toronto_montreal.groupby(['train_id', 'instance'])

# Create lists to store the delay data
kingston_delays = []
montreal_delays_relative = []
train_info = []

# For each train instance, extract Kingston arrival delay and Montreal arrival delay
for (train_id, instance), group in train_instances:
    # Sort by stop_id to ensure proper order
    group = group.sort_values('stop_id')
    
    # Find Kingston stop (arrival delay)
    kingston = group[group['code'] == 'KGON']
    
    # Find Montreal stop (arrival delay)
    montreal = group[group['code'] == 'MTRL']
    
    # If both stops exist, record the delays
    if not kingston.empty and not montreal.empty:
        kingston_delay = kingston['diffMin'].values[0]
        montreal_delay_absolute = montreal['diffMin'].values[0]
        # Calculate relative delay: additional delay accumulated from Kingston to Montreal
        montreal_delay_relative = montreal_delay_absolute - kingston_delay
        
        kingston_delays.append(kingston_delay)
        montreal_delays_relative.append(montreal_delay_relative)
        train_info.append({
            'train_id': train_id,
            'instance': instance,
            'kingston_delay': kingston_delay,
            'montreal_delay_absolute': montreal_delay_absolute,
            'montreal_delay_relative': montreal_delay_relative
        })

# Create a DataFrame with the results
delay_df = pd.DataFrame(train_info)

# Save the processed data
delay_df.to_csv('toronto_montreal_delay_analysis.csv', index=False)

print(f"Total train instances analyzed: {len(delay_df)}")
print(f"\nKingston Arrival Delay Statistics:")
print(f"  Mean: {np.mean(kingston_delays):.2f} minutes")
print(f"  Median: {np.median(kingston_delays):.2f} minutes")
print(f"  Std Dev: {np.std(kingston_delays):.2f} minutes")
print(f"\nMontreal Relative Delay Statistics (additional delay from Kingston to Montreal):")
print(f"  Mean: {np.mean(montreal_delays_relative):.2f} minutes")
print(f"  Median: {np.median(montreal_delays_relative):.2f} minutes")
print(f"  Std Dev: {np.std(montreal_delays_relative):.2f} minutes")

# Calculate correlation
correlation = np.corrcoef(kingston_delays, montreal_delays_relative)[0, 1]
print(f"\nCorrelation between Kingston delay and Montreal relative delay: {correlation:.3f}")

# Create the scatter plot
plt.figure(figsize=(12, 8))
plt.scatter(kingston_delays, montreal_delays_relative, alpha=0.5, s=50, edgecolors='black', linewidth=0.5)

# Add trend line
z = np.polyfit(kingston_delays, montreal_delays_relative, 1)
p = np.poly1d(z)
plt.plot(sorted(kingston_delays), p(sorted(kingston_delays)), 
         "r--", linewidth=2, label=f'Trend line: y = {z[0]:.2f}x + {z[1]:.2f}')

# Add horizontal line (y=0) to show where no additional delay is added
min_x = min(kingston_delays)
max_x = max(kingston_delays)
plt.axhline(y=0, color='g', linestyle='--', alpha=0.5, linewidth=1.5, label='y = 0 (no additional delay)')

plt.xlabel('Kingston Arrival Delay (minutes)', fontsize=12, fontweight='bold')
plt.ylabel('Additional Delay from Kingston to Montreal (minutes)', fontsize=12, fontweight='bold')
plt.title('Impact of Kingston Arrival Delay on Additional Delay to Montreal\nToronto → Kingston → Montreal', 
          fontsize=14, fontweight='bold', pad=20)
plt.grid(True, alpha=0.3, linestyle='--')
plt.legend(fontsize=10)

# Add correlation text
plt.text(0.05, 0.95, f'Correlation: {correlation:.3f}\nn = {len(kingston_delays)} trains', 
         transform=plt.gca().transAxes, fontsize=11, 
         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig('toronto_montreal_delay_scatter.png', dpi=300, bbox_inches='tight')
print("\nScatter plot saved as 'toronto_montreal_delay_scatter.png'")
plt.show()

# Additional analysis: show sample of the data
print("\nSample of the data:")
print(delay_df.head(10))
