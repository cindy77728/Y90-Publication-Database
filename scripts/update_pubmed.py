#!/usr/bin/env python3
"""Weekly PubMed updater for Y90 Publication Database.

This script searches PubMed for recent Y-90/radioembolization publications,
adds new records to publications.json, and lets GitHub Actions commit the update.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "publications.json"

QUERY = '"Y-90"[tiab] OR "Y90"[tiab] OR "yttrium-90"[tiab] OR "yttrium 90"[tiab] OR "radioembolization"[tiab] OR "radio-embolization"[tiab] OR "SIRT"[tiab] OR "selective internal radiation therapy"[tiab] OR "yttrium-90 microspheres"[tiab] OR "Y-90 microspheres"[tiab]'


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "Y90PublicationDatabase/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def normalize_title(title: str) -> str:
    text = re.sub(r"<[^>]+>", "", title or "")
    text = text.lower().replace("’", "").replace("'", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def load_data() -> dict:
    if not DATA_FILE.exists():
        return {"last_updated": None, "publications": []}
    try:
        payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"last_updated": None, "publications": []}
    if isinstance(payload, list):
        return {"last_updated": None, "publications": payload}
    payload.setdefault("publications", [])
    return payload


def get_recent_pmids(days: int = 7, retmax: int = 50) -> list[str]:
    params = urllib.parse.urlencode({
        "db": "pubmed",
        "term": QUERY,
        "reldate": str(days),
        "datetype": "pdat",
        "retmax": str(retmax),
        "retmode": "json",
        "sort": "date",
    })
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{params}"
    data = fetch_json(url)
    return data.get("esearchresult", {}).get("idlist", [])


def get_summaries(pmids: list[str]) -> dict:
    if not pmids:
        return {}
    params = urllib.parse.urlencode({
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "json",
    })
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?{params}"
    data = fetch_json(url)
    return data.get("result", {})


def get_pmc_map(pmids: list[str]) -> dict[str, str]:
    if not pmids:
        return {}
    params = urllib.parse.urlencode({
        "dbfrom": "pubmed",
        "db": "pmc",
        "id": ",".join(pmids),
        "retmode": "json",
    })
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?{params}"
    try:
        data = fetch_json(url)
    except Exception as exc:
        print(f"PMC lookup failed: {exc}")
        return {}
    pmc_map = {}
    for linkset in data.get("linksets", []):
        ids = linkset.get("ids") or []
        if not ids:
            continue
        pmid = str(ids[0])
        for db in linkset.get("linksetdbs", []) or []:
            if db.get("linkname") == "pubmed_pmc" and db.get("links"):
                pmc_map[pmid] = "PMC" + str(db["links"][0])
                break
    return pmc_map


def infer_year(pubdate: str) -> int:
    m = re.search(r"(19|20)\d{2}", pubdate or "")
    return int(m.group(0)) if m else dt.datetime.utcnow().year


def make_record(summary: dict, pmcid: str, next_id: int) -> dict:
    pmid = str(summary.get("uid", ""))
    title = re.sub(r"<[^>]+>", "", summary.get("title") or "Unknown title").strip()
    authors_list = summary.get("authors") or []
    authors = ", ".join(a.get("name", "") for a in authors_list[:3] if a.get("name"))
    if len(authors_list) > 3:
        authors += ", et al."
    journal = summary.get("source") or ""
    year = infer_year(summary.get("pubdate", ""))
    return {
        "id": next_id,
        "year": year,
        "title": title,
        "authors": authors,
        "journal": journal,
        "country": "",
        "product": "ns",
        "categories": ["PubMed Updates"],
        "primaryCategory": "PubMed Updates",
        "results": "",
        "findings": "Auto-added from weekly PubMed search. Please review the abstract/full text and replace this with curated key findings.",
        "notes": "Auto-added by GitHub Actions weekly PubMed update. Needs human review before internal or external use.",
        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
        "pmcid": pmcid,
        "pdfUrl": f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/pdf/" if pmcid else "",
        "pdfFileName": "",
        "pdfData": None,
        "abstract": "",
        "reviewStatus": "AI Draft",
        "pmid": pmid,
    }


def main() -> int:
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    payload = load_data()
    publications = payload.get("publications", [])

    existing_pmids = {str(p.get("pmid") or "").strip() for p in publications if p.get("pmid")}
    for p in publications:
        url = str(p.get("url") or "")
        m = re.search(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)", url)
        if m:
            existing_pmids.add(m.group(1))
    existing_titles = {normalize_title(p.get("title", "")) for p in publications if p.get("title")}
    max_id = max([int(p.get("id") or 0) for p in publications] + [900000])

    pmids = get_recent_pmids(days=days)
    if not pmids:
        print(f"No recent PubMed records found in the last {days} days.")
        payload["last_checked"] = dt.datetime.utcnow().isoformat(timespec="seconds") + "Z"
        DATA_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return 0

    time.sleep(0.34)
    summaries = get_summaries(pmids)
    time.sleep(0.34)
    pmc_map = get_pmc_map(pmids)

    added = 0
    for pmid in pmids:
        if pmid in existing_pmids:
            continue
        summary = summaries.get(pmid)
        if not summary:
            continue
        title_key = normalize_title(summary.get("title", ""))
        if title_key and title_key in existing_titles:
            continue
        max_id += 1
        publications.append(make_record(summary, pmc_map.get(pmid, ""), max_id))
        existing_pmids.add(pmid)
        existing_titles.add(title_key)
        added += 1

    payload["last_checked"] = dt.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    if added:
        payload["last_updated"] = payload["last_checked"]
    payload["publications"] = publications
    DATA_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Checked {len(pmids)} PubMed records. Added {added} new publication(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
