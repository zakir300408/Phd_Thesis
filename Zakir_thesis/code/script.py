import json
import webbrowser
from pathlib import Path

PAPERS1_PATH = Path("papers.json")  # existing collection
PAPERS2_PATH = Path("papers2.json")  # new collection to be filtered/processed

def load_papers(path: Path):
    """Load papers from a file. Accepts either a list (top-level) or {"papers": [...]}."""
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "papers" in data:
        return data["papers"]
    if isinstance(data, list):
        return data
    raise ValueError(f"Unsupported JSON structure in {path}")

def save_papers_list(path: Path, papers_list):
    """Save a top-level list to the given path (pretty-printed)."""
    with path.open("w", encoding="utf-8") as f:
        json.dump(papers_list, f, ensure_ascii=False, indent=2)

def main():
    # Load existing and new lists
    if not PAPERS1_PATH.exists():
        print(f"Warning: {PAPERS1_PATH} not found. Treating as empty.")
        existing_papers = []
    else:
        existing_papers = load_papers(PAPERS1_PATH)
    if not PAPERS2_PATH.exists():
        print(f"Error: {PAPERS2_PATH} not found. Nothing to process.")
        return
    new_papers = load_papers(PAPERS2_PATH)

    existing_dois = {p.get("doi") for p in existing_papers if p.get("doi")}

    # Filter new_papers: keep entries whose doi is not in existing_dois.
    filtered = []
    seen = set()
    for p in new_papers:
        doi = p.get("doi")
        # Keep entries without DOI (they won't be opened), but still include them unless
        # you explicitly want to remove them; only remove entries that have DOIs present in existing.
        if doi and doi in existing_dois:
            # drop common entry
            continue
        # deduplicate by DOI (or by full dict if no doi)
        key = doi if doi else json.dumps(p, sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        filtered.append(p)

    # Overwrite papers2.json with filtered list (common DOIs removed)
    save_papers_list(PAPERS2_PATH, filtered)
    print(f"Filtered papers2.json: kept {len(filtered)} entries (removed common DOIs).")

    # Now process DOIs from the filtered list
    papers_to_process = [p for p in filtered if p.get("doi")]
    if not papers_to_process:
        print("No DOIs to process in the filtered papers2.json.")
        return

    print(f"Processing {len(papers_to_process)} DOIs from {PAPERS2_PATH}")
    print("For each one, I will open the DOI URL in your default browser.")
    print("You handle login/download, then come back here and press Enter for the next paper.\n")

    for i, paper in enumerate(papers_to_process, start=1):
        doi = paper.get("doi")
        title = paper.get("title", "(no title)")
        url = f"https://doi.org/{doi}"
        print(f"[{i}/{len(papers_to_process)}] Opening:")
        print(f"  Title: {title}")
        print(f"  DOI:   {doi}")
        print(f"  URL:   {url}")

        webbrowser.open_new_tab(url)
        input("Press Enter here in the terminal to move to the next paper...")

    print("Done. All DOIs from filtered papers2.json processed.")

if __name__ == "__main__":
    main()
