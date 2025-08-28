import argparse
import csv
import os
import requests

def parse_args():
    parser = argparse.ArgumentParser(description="Update final raw gist with new dorks")
    parser.add_argument('--local-csv', required=True, help='Local CSV file path')
    parser.add_argument('--gist-id', required=True, help='Final gist ID')
    parser.add_argument('--token', required=False, help='GitHub token, or use GH_TOKEN env variable')
    return parser.parse_args()

def read_csv(filepath):
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        return [row[0].strip() for row in reader if row]

def fetch_gist_content(gist_id, token):
    headers = {"Authorization": f"token {token}"} if token else {}
    url = f"https://api.github.com/gists/{gist_id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    files = response.json()['files']
    content = list(files.values())[0]['content']
    lines = content.split('\n')[1:]
    return [line.strip() for line in lines if line.strip()]

def merge_dorks(old_dorks, new_dorks):
    return list(set(old_dorks) | set(new_dorks))

def update_gist(gist_id, token, dorks):
    headers = {"Authorization": f"token {token}"} if token else {}
    url = f"https://api.github.com/gists/{gist_id}"
    content = "dork\n" + "\n".join(sorted(dorks))
    payload = {
        "files": {
            "wordpress_raw_dorks.csv": {"content": content}
        }
    }
    response = requests.patch(url, json=payload, headers=headers)
    response.raise_for_status()

def main():
    args = parse_args()
    token = args.token or os.getenv('GH_TOKEN')
    if not token:
       raise ValueError("GitHub token not provided")
    local_dorks = read_csv(args.local_csv)
    old_gist_dorks = fetch_gist_content(args.gist_id, token)
    combined_dorks = merge_dorks(old_gist_dorks, local_dorks)
    update_gist(args.gist_id, token, combined_dorks)
    print(f"Updated final gist with {len(combined_dorks)} total dorks.")

if __name__ == '__main__':
    main()
