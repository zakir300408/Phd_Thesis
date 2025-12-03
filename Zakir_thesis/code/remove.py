import json
import os
import string

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(obj, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

def normalize_title(title):
    if not title:
        return None
    # lower, strip, remove punctuation and collapse spaces
    t = title.lower().strip()
    table = str.maketrans("", "", string.punctuation)
    t = t.translate(table)
    t = " ".join(t.split())
    return t

def build_existing_keys(papers_list, title_key="title", doi_key="doi"):
    keys = set()
    for p in papers_list:
        doi = (p.get(doi_key) or "").strip().lower()
        if doi:
            keys.add(f"doi:{doi}")
        title = normalize_title(p.get(title_key))
        if title:
            keys.add(f"title:{title}")
    return keys

def is_techarxiv(paper):
    # check typical fields for "techarxiv"
    for key in ["venue", "journal", "source"]:
        val = paper.get(key)
        if isinstance(val, str) and "techarxiv" in val.lower():
            return True
    return False

def get_year(paper):
    y = paper.get("year")
    try:
        return int(y)
    except Exception:
        return None

def main(
    papers_path="papers.json",
    papers2_path="papers2.json",
    papers3_path="papers3.json",
    output_path="papers3_filtered.json",
):
    # 1) load
    data1 = load_json(papers_path)          # expects {"papers": [...]}
    data2 = load_json(papers2_path)         # expects [...]
    data3 = load_json(papers3_path)         # expects {"papers": [...]}

    papers1 = data1.get("papers", [])
    papers2 = data2 if isinstance(data2, list) else data2.get("papers", [])
    papers3 = data3.get("papers", [])

    # 2) build key set from papers1 + papers2
    existing_keys = set()
    existing_keys |= build_existing_keys(papers1, title_key="title", doi_key="doi")
    existing_keys |= build_existing_keys(papers2, title_key="title", doi_key="doi")

    # 3) filter papers3
    filtered_papers3 = []
    for p in papers3:
        # skip if techarxiv
        if is_techarxiv(p):
            continue

        # skip if before 2018
        year = get_year(p)
        if year is not None and year < 2018:
            continue

        # build keys for duplication check
        keys_for_p = set()
        doi = (p.get("doi") or "").strip().lower()
        if doi:
            keys_for_p.add(f"doi:{doi}")
        title = normalize_title(p.get("title"))
        if title:
            keys_for_p.add(f"title:{title}")

        # skip if any key already exists
        if any(k in existing_keys for k in keys_for_p):
            continue

        # otherwise keep and also add to existing_keys to avoid duplicates inside papers3
        existing_keys |= keys_for_p
        filtered_papers3.append(p)

    # 4) write out new json
    out_obj = {"papers": filtered_papers3}
    save_json(out_obj, output_path)

    print(f"Original papers3 count: {len(papers3)}")
    print(f"Filtered papers3 count: {len(filtered_papers3)}")
    print(f"Saved filtered file to: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    main()
