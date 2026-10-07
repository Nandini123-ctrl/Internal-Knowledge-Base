import csv
from datetime import datetime, timezone

def save_to_csv():
    # Sample structured rows simulating your final pipeline output
    rows = [
        {"Category": "Research Paper", "Title": "JarvisGUI: Towards Cross-Device GUI Agents", "Entity": "Openai", "Stars": 247727, "Timestamp": datetime.now(timezone.utc).isoformat()},
        {"Category": "Research Paper", "Title": "ConvMem: Convolutional Memory for Long-Context", "Entity": "Anthropic", "Stars": 0, "Timestamp": datetime.now(timezone.utc).isoformat()}
    ]
    
    filename = "frontier_atlas_output.csv"
    fields = ["Category", "Title", "Entity", "Stars", "Timestamp"]
    
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            
    print(f"Successfully exported data to {filename}!")

if __name__ == "__main__":
    save_to_csv()
