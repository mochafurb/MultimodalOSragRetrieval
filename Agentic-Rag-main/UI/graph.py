import matplotlib.pyplot as plt

# Operating System IPC Throughput Benchmarks (GB/s)
mechanisms = ['Shared Memory', 'UNIX Domain Socket', 'Anonymous Pipe', 'POSIX Message Queue', 'TCP Loopback']
throughput_gb_s = [35.0, 4.2, 2.5, 1.8, 1.1]

# OS Dashboard Colors
colors = ['#2563EB', '#0EA5E9', '#10B981', '#F59E0B', '#64748B']

# Create the bar chart
fig, ax = plt.subplots(figsize=(8, 4.5))
bars = ax.bar(mechanisms, throughput_gb_s, color=colors)

# Set the title and labels
ax.set_title('OS Interprocess Communication (IPC) Throughput Comparison (GB/s)', fontsize=12, fontweight='bold', pad=12)
ax.set_xlabel('IPC Mechanism', fontweight='medium')
ax.set_ylabel('Bandwidth (GB/s)', fontweight='medium')

# Add value labels on top of bars
for bar in bars:
    height = bar.get_height()
    ax.annotate(f'{height:.1f} GB/s',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha='center', va='bottom', fontsize=8.5, fontweight='bold')

plt.xticks(rotation=20, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()