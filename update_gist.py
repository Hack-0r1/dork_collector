import argparse
import csv
import requests

def parse_args():
    parser = argparse.ArgumentParser(description="Update final raw gist with new dorks")
    parser.add_argument('--local-csv', required=True, help='Local CSV file path')
    parser.add_argument('--gist-id', required=True, help='Final gist ID')
    parser.add_argument('--token', required=True, help='GitHub token for authentication')
    return parser.parse_args()

def read_csv(filepath):
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        rows = [row[0].strip() for row in reader if row]
    return rows

def fetch_gist_content(gist_id, token):
    url = f"https://api.github.com/gists/{gist_id}"
    headers = {'Authorization': f'token {token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    files = response.json()['files']
    # Assuming single file, get its content
    file_content = list(files.values())[0]['content']
    return file_content.splitlines()[1:]  # skip header line

def merge_dorks(old_dorks, new_dorks):
    return list(set(old_dorks) | set(new_dorks))

def update_gist(gist_id, token, dorks):
    url = f"https://api.github.com/gists/{gist_id}"
    headers = {'Authorization': f'token {token}'}
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
    local_dorks = read_csv(args.local_csv)
    old_gist_dorks = fetch_gist_content(args.gist_id, args.token)
    combined_dorks = merge_dorks(old_gist_dorks, local_dorks)
    update_gist(args.gist_id, args.token, combined_dorks)
    print(f"Updated final gist with {len(combined_dorks)} total dorks.")

if __name__ == '__main__':
    main()
