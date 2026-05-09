# -*- coding: utf-8 -*-
"""
Download product images for the Tunghsun product CSV.

This script reads the product CSV, searches image engines for each product,
downloads the first usable image, and writes an updated CSV with the `images`
column filled.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import mimetypes
import random
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_CSV_FILE = "\u540c\u6d35\u7db2\u7ad9\u7522\u54c1\u6e05\u55ae.csv"
DEFAULT_OUTPUT_CSV = "updated_products.csv"
DEFAULT_OUTPUT_DIR = "images"
DEFAULT_REPORT_FILE = "image_download_report.csv"
TIMEOUT_SECONDS = 25

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/137.0 Safari/537.36"
)

IMAGE_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "image/avif": ".avif",
}

SKIP_URL_PARTS = (
    "logo",
    "icon",
    "banner",
    "avatar",
    "emoji",
    "sprite",
    "placeholder",
)

PREFERRED_URL_PARTS = (
    "kkl.com.tw",
    "k38.com.tw",
    "alcohol.com.tw",
    "my9.com.tw",
    "goldenfull.shop",
    "77whiskyshop.com",
)

SHOP_URL_PARTS = (
    "shop",
    "store",
    "product",
    "catalog",
    "goods",
    "item",
    "whisky",
    "alcohol",
)


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def sanitize_filename(value: str, fallback: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r'[\\/:*?"<>|]', " ", value)
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"[^\w\-\u4e00-\u9fff]", "-", value)
    value = re.sub(r"-+", "-", value).strip("-_ ")
    return value or fallback


def normalize_product_name(value: str) -> str:
    return (
        (value or "")
        .replace("\uff08", "(")
        .replace("\uff09", ")")
        .replace("\u3000", " ")
        .strip()
    )


def product_without_parentheses(value: str) -> str:
    return re.sub(r"[\uff08(][^\uff09)]*[\uff09)]", "", value or "").strip()


def build_search_query(row: dict[str, str]) -> str:
    category = (row.get("category") or "").strip()
    product = normalize_product_name(row.get("product") or "")
    short_product = product_without_parentheses(product)

    parts = []
    if product:
        parts.append(f'"{product}"')
    if short_product and short_product != product:
        parts.append(f'"{short_product}"')
    if category:
        parts.append(f'"{category}"')
    parts.append("\u5546\u54c1 \u9152\u74f6 \u5716\u7247 -\u65c5\u904a -\u666f\u9ede -\u6230\u8eca")
    return " ".join(parts)


def request_url(url: str, referer: str | None = None) -> bytes:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.7,en;q=0.6",
    }
    if referer:
        headers["Referer"] = referer

    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return response.read()


def compact_text(value: str) -> str:
    return re.sub(r"[\s\W_]+", "", value or "", flags=re.UNICODE).lower()


def duckduckgo_image_search(query: str, max_candidates: int) -> list[dict[str, str]]:
    search_url = "https://duckduckgo.com/?" + urllib.parse.urlencode(
        {
            "q": query,
            "iax": "images",
            "ia": "images",
            "kl": "tw-tzh",
        }
    )
    html_text = request_url(search_url).decode("utf-8", errors="replace")
    vqd_match = re.search(r"vqd=['\"]([^'\"]+)['\"]", html_text)
    if not vqd_match:
        vqd_match = re.search(r"vqd=([\d-]+)&", html_text)
    if not vqd_match:
        raise ValueError("DuckDuckGo did not return a vqd token")

    vqd = vqd_match.group(1)
    candidates: list[dict[str, str]] = []
    next_url = "https://duckduckgo.com/i.js?" + urllib.parse.urlencode(
        {
            "l": "tw-tzh",
            "o": "json",
            "q": query,
            "vqd": vqd,
            "f": ",,,",
            "p": "1",
        }
    )

    while next_url and len(candidates) < max_candidates:
        payload = json.loads(request_url(next_url, referer=search_url).decode("utf-8", errors="replace"))
        for result in payload.get("results", []):
            image_url = result.get("image") or result.get("thumbnail")
            if isinstance(image_url, str):
                add_candidate(
                    candidates,
                    image_url,
                    {
                        "title": result.get("title", ""),
                        "purl": result.get("url", ""),
                        "source": result.get("source", ""),
                    },
                )
            if len(candidates) >= max_candidates:
                break

        raw_next = payload.get("next")
        next_url = urllib.parse.urljoin("https://duckduckgo.com", raw_next) if raw_next else ""

    return candidates


def bing_image_search(query: str, max_candidates: int) -> list[dict[str, str]]:
    params = urllib.parse.urlencode(
        {
            "q": query,
            "form": "HDRSC2",
            "first": "1",
            "tsc": "ImageBasicHover",
        }
    )
    search_url = f"https://www.bing.com/images/search?{params}"
    html_text = request_url(search_url).decode("utf-8", errors="replace")

    candidates: list[dict[str, str]] = []

    # Bing stores the original image URL inside the HTML-escaped `m` JSON
    # attribute of result anchors. The older script only inspected <img src>,
    # which usually returns thumbnails or no useful result.
    for raw_json in re.findall(r'\bm="([^"]+)"', html_text):
        try:
            metadata = json.loads(html.unescape(raw_json))
        except json.JSONDecodeError:
            continue

        image_url = metadata.get("murl") or metadata.get("turl")
        if isinstance(image_url, str):
            add_candidate(candidates, image_url, metadata)
        if len(candidates) >= max_candidates:
            return candidates

    # Fallback for HTML variants.
    for raw_url in re.findall(r'"murl"\s*:\s*"([^"]+)"', html_text):
        image_url = raw_url.encode("utf-8").decode("unicode_escape")
        add_candidate(candidates, image_url, {"murl": image_url})
        if len(candidates) >= max_candidates:
            break

    return candidates


def image_search(engine: str, query: str, max_candidates: int) -> list[dict[str, str]]:
    if engine == "duckduckgo":
        return duckduckgo_image_search(query, max_candidates)
    if engine == "bing":
        return bing_image_search(query, max_candidates)
    raise ValueError(f"unsupported search engine: {engine}")


def add_candidate(candidates: list[dict[str, str]], image_url: str, metadata: dict[str, Any]) -> None:
    image_url = html.unescape(image_url).strip()
    lower_url = image_url.lower()

    if not image_url.startswith(("http://", "https://")):
        return
    if any(part in lower_url for part in SKIP_URL_PARTS):
        return
    if any(candidate["url"] == image_url for candidate in candidates):
        return

    candidates.append(
        {
            "url": image_url,
            "title": str(metadata.get("t") or metadata.get("title") or ""),
            "page_url": str(metadata.get("purl") or metadata.get("p") or ""),
            "source": str(metadata.get("s") or ""),
        }
    )


def score_candidate(row: dict[str, str], candidate: dict[str, str]) -> tuple[int, str]:
    category = compact_text(row.get("category", ""))
    product = compact_text(normalize_product_name(row.get("product", "")))
    short_product = compact_text(product_without_parentheses(normalize_product_name(row.get("product", ""))))
    haystack = compact_text(
        " ".join(
            [
                candidate.get("title", ""),
                candidate.get("page_url", ""),
                candidate.get("source", ""),
                candidate.get("url", ""),
            ]
        )
    )
    raw_haystack = " ".join(
        [
            candidate.get("title", ""),
            candidate.get("page_url", ""),
            candidate.get("source", ""),
            candidate.get("url", ""),
        ]
    ).lower()

    score = 0
    reasons = []
    if product and product in haystack:
        score += 120
        reasons.append("product")
    if short_product and short_product != product and short_product in haystack:
        score += 90
        reasons.append("short_product")
    if category and category in haystack:
        score += 20
        reasons.append("category")

    volume_match = re.search(r"(\d+)\s*(?:ml|ML|l|L)", row.get("product", ""))
    if volume_match and volume_match.group(1) in haystack:
        score += 35
        reasons.append("volume")
    if any(part in raw_haystack for part in PREFERRED_URL_PARTS):
        score += 45
        reasons.append("preferred_source")
    if any(part in raw_haystack for part in SHOP_URL_PARTS):
        score += 20
        reasons.append("shop_source")
    if re.search(r"\b(?:img|image|upload|uploads|cdn|files)\b", raw_haystack):
        score += 10
        reasons.append("image_host")

    return score, "+".join(reasons) or "no metadata match"


def extension_for(url: str, content_type: str | None) -> str:
    if content_type:
        normalized = content_type.split(";")[0].strip().lower()
        if normalized in IMAGE_EXTENSIONS:
            return IMAGE_EXTENSIONS[normalized]

    suffix = Path(urllib.parse.urlparse(url).path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}:
        return ".jpg" if suffix == ".jpeg" else suffix

    guessed = mimetypes.guess_extension(content_type or "")
    if guessed in IMAGE_EXTENSIONS.values():
        return guessed
    return ".jpg"


def download_image(url: str, destination_base: Path, force: bool) -> Path:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        content_type = response.headers.get("Content-Type", "")
        if not content_type.lower().startswith("image/"):
            raise ValueError(f"not an image response: {content_type or 'unknown'}")

        extension = extension_for(url, content_type)
        destination = destination_base.with_suffix(extension)
        if destination.exists() and not force:
            return destination

        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(response.read())
        return destination


def main() -> None:
    parser = argparse.ArgumentParser(description="Download product images and update the product CSV.")
    parser.add_argument("--csv-file", default=DEFAULT_CSV_FILE)
    parser.add_argument("--output-csv", default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-file", default=DEFAULT_REPORT_FILE)
    parser.add_argument("--search-engine", choices=("duckduckgo", "bing"), default="duckduckgo")
    parser.add_argument("--max-products", type=int, default=0, help="0 means process all products.")
    parser.add_argument("--max-candidates", type=int, default=8)
    parser.add_argument("--min-score", type=int, default=80)
    parser.add_argument("--delay-min", type=float, default=1.2)
    parser.add_argument("--delay-max", type=float, default=2.6)
    parser.add_argument("--candidates-only", action="store_true", help="Only write candidate scores, do not download.")
    parser.add_argument("--force", action="store_true", help="Download again even if a local image exists.")
    args = parser.parse_args()

    csv_file = Path(args.csv_file)
    output_csv = Path(args.output_csv)
    output_dir = Path(args.output_dir)
    report_file = Path(args.report_file)

    rows, fieldnames = read_csv(csv_file)
    required_columns = {"category", "product", "product_slug"}
    missing_columns = sorted(required_columns.difference(fieldnames))
    if missing_columns:
        raise SystemExit(f"CSV is missing required columns: {', '.join(missing_columns)}")
    if "images" not in fieldnames:
        fieldnames.append("images")
        for row in rows:
            row["images"] = ""

    report_rows: list[dict[str, str]] = []
    processed_count = 0
    total = len(rows)

    print(f"Reading CSV: {csv_file}")
    print(f"Products: {total}")
    print("=" * 60)

    for index, row in enumerate(rows, start=1):
        product_name = normalize_product_name(row.get("product", ""))
        product_slug = sanitize_filename(row.get("product_slug", ""), f"product-{index}")
        existing_image = (row.get("images") or "").strip()

        if not product_name:
            report_rows.append(report(index, product_name, "Skipped: missing product", "", "", ""))
            continue
        if args.max_products > 0 and processed_count >= args.max_products:
            break

        processed_count += 1
        destination_base = output_dir / product_slug
        print(f"[{index}/{total}] {product_name}")

        if existing_image and not args.force:
            print(f"  skipped: images already set ({existing_image})")
            report_rows.append(report(index, product_name, "Skipped: images already set", existing_image, "", ""))
            continue

        local_matches = sorted(output_dir.glob(f"{product_slug}.*"), key=lambda path: path.stat().st_mtime, reverse=True)
        if local_matches and not args.force:
            relative_path = local_matches[0].as_posix()
            row["images"] = relative_path
            print(f"  using existing file: {relative_path}")
            report_rows.append(report(index, product_name, "Existing file", relative_path, "", ""))
            continue

        query = build_search_query(row)
        print(f"  searching {args.search_engine}: {query}")

        try:
            candidates = image_search(args.search_engine, query, args.max_candidates)
        except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            message = f"Search failed: {exc}"
            print(f"  {message}")
            report_rows.append(report(index, product_name, message, "", "", query))
            continue

        if not candidates:
            print("  no image candidates found")
            report_rows.append(report(index, product_name, "No image candidates found", "", "", query))
            continue

        ranked_candidates = []
        for candidate in candidates:
            score, reason = score_candidate(row, candidate)
            ranked_candidates.append((score, reason, candidate))
            if args.candidates_only:
                report_rows.append(
                    report(
                        index,
                        product_name,
                        f"Candidate score {score}: {reason}",
                        "",
                        candidate["url"],
                        query,
                    )
                )

        ranked_candidates.sort(key=lambda item: item[0], reverse=True)

        if args.candidates_only:
            print(f"  wrote {len(ranked_candidates)} candidate scores")
            if args.delay_max > 0:
                time.sleep(random.uniform(args.delay_min, args.delay_max))
            continue

        saved_path = None
        saved_url = ""
        last_error = ""
        for score, reason, candidate in ranked_candidates:
            image_url = candidate["url"]
            if score < args.min_score:
                report_rows.append(
                    report(
                        index,
                        product_name,
                        f"Rejected: score {score} below {args.min_score} ({reason})",
                        "",
                        image_url,
                        query,
                    )
                )
                continue

            try:
                saved_path = download_image(image_url, destination_base, args.force)
                saved_url = image_url
                break
            except Exception as exc:  # noqa: BLE001 - continue to next image candidate.
                last_error = str(exc)
                report_rows.append(
                    report(
                        index,
                        product_name,
                        f"Download failed: score {score} ({reason}): {last_error}",
                        "",
                        image_url,
                        query,
                    )
                )

        if saved_path:
            relative_path = saved_path.as_posix()
            row["images"] = relative_path
            print(f"  downloaded: {relative_path}")
            report_rows.append(report(index, product_name, "Downloaded", relative_path, saved_url, query))
        else:
            message = f"no candidate passed score {args.min_score}"
            if last_error:
                message = f"{message}; last download error: {last_error}"
            print(f"  {message}")
            report_rows.append(report(index, product_name, message, "", "", query))

        if args.delay_max > 0:
            time.sleep(random.uniform(args.delay_min, args.delay_max))

    write_csv(output_csv, rows, fieldnames)
    write_csv(report_file, report_rows, ["row", "product", "status", "file", "url", "query"])

    print()
    print("=" * 60)
    print(f"Updated CSV written: {output_csv}")
    print(f"Report written: {report_file}")
    print("=" * 60)


def report(row: int, product: str, status: str, file: str, url: str, query: str) -> dict[str, str]:
    return {
        "row": str(row),
        "product": product,
        "status": status,
        "file": file,
        "url": url,
        "query": query,
    }


if __name__ == "__main__":
    main()
