import argparse
import csv
import os
import requests

def parse_args():
    parser = argparse.ArgumentParser(description="Collect WordPress Google dorks")
    parser.add_argument('--stack', required=True, help='Stack type e.g. wordpress')
    parser.add_argument('--seed-file', required=True, help='Path to seed dork queries file')
    parser.add_argument('--raw-gist-id', required=True, help='Gist ID for temp CSV storage')
    parser.add_argument('--max-results', type=int, default=50, help='Max results to fetch')
    return parser.parse_args()

def load_seeds(seed_file):
    with open(seed_file, 'r') as f:
        seeds = [line.strip() for line in f if line.strip()]
    return seeds

def fetch_dorks(seeds, max_results):
    # Your actual data harvesting logic here; currently returns limited seeds.
    return seeds[:max_results]

def fetch_existing_dorks_from_gist(gist_id):
    token = os.getenv('GH_TOKEN')
    headers = {"Authorization": f"token {token}"} if token else {}
    url = f"https://api.github.com/gists/{gist_id}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Warning: Could not fetch gist {gist_id} (status {response.status_code})")
        return []
    files = response.json()['files']
    content = list(files.values())[0]['content']
    lines = content.split('\n')[1:]  # skip header
    return [line.strip() for line in lines if line.strip()]

def merge_dorks(existing, new):
    return list(set(existing) | set(new))

def save_to_csv(dorks, filename='wptemp.csv'):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['dork'])
        for dork in dorks:
            writer.writerow([dork])

def main():
    args = parse_args()
    seeds = load_seeds(args.seed_file)
    existing_dorks = fetch_existing_dorks_from_gist(args.raw_gist_id)
    new_dorks = fetch_dorks(seeds, args.max_results)
    combined = merge_dorks(existing_dorks, new_dorks)
    save_to_csv(combined)
    print(f"Collected {len(combined)} total dorks.")

if __name__ == '__main__':
    main()
