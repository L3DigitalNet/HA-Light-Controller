#!/usr/bin/env python3
"""Verify all links in markdown documentation files."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import TypedDict


class LinkInfo(TypedDict):
    """Information about a link."""

    file: Path
    line: int
    text: str
    target: str
    link_type: str  # 'internal', 'external', 'anchor'


def find_markdown_files(root: Path) -> list[Path]:
    """Find all markdown files excluding venv and hidden directories."""
    files: list[Path] = []
    for md_file in root.rglob("*.md"):
        # Skip venv, hidden dirs, and .cache
        parts = md_file.relative_to(root).parts
        if any(
            p.startswith(".")
            or p == "venv"
            or p == "__pycache__"
            or p == "node_modules"
            for p in parts
        ):
            continue
        files.append(md_file)
    return sorted(files)


def extract_links(file_path: Path) -> list[LinkInfo]:
    """Extract all markdown links from a file."""
    links: list[LinkInfo] = []
    content = file_path.read_text(encoding="utf-8")

    # Pattern for markdown links: [text](url)
    # Handles URLs with or without anchors
    pattern = r"\[([^\]]+)\]\(([^)]+)\)"

    for line_num, line in enumerate(content.splitlines(), start=1):
        # Skip links inside inline code (backticks)
        # Remove content within backticks before processing
        line_without_code = re.sub(r"`[^`]+`", "", line)

        for match in re.finditer(pattern, line_without_code):
            text = match.group(1)
            target = match.group(2)

            # Determine link type
            if target.startswith(("http://", "https://", "mailto:")):
                link_type = "external"
            elif target.startswith("#"):
                link_type = "anchor"
            else:
                link_type = "internal"

            links.append(
                {
                    "file": file_path,
                    "line": line_num,
                    "text": text,
                    "target": target,
                    "link_type": link_type,
                }
            )

    return links


def verify_internal_link(source_file: Path, target: str, root: Path) -> bool:
    """Verify an internal file link exists."""
    # Remove anchor if present
    target_path = target.split("#")[0]

    if not target_path:  # Pure anchor link
        return True

    # Resolve relative to source file's directory
    source_dir = source_file.parent
    full_path = (source_dir / target_path).resolve()

    # Check if file exists
    return full_path.exists()


def verify_anchor_link(source_file: Path, anchor: str) -> bool:
    """Verify an anchor link exists in the same file."""
    # Remove leading #
    anchor_name = anchor.lstrip("#").lower()

    # Read file and generate anchors from headers
    content = source_file.read_text(encoding="utf-8")
    header_pattern = r"^#{1,6}\s+(.+)$"

    for line in content.splitlines():
        match = re.match(header_pattern, line)
        if match:
            header_text = match.group(1)
            # Generate GitHub-style anchor
            # Remove markdown formatting
            header_text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", header_text)
            # Convert to lowercase
            generated_anchor = header_text.lower()
            # Remove special characters (GitHub removes &, etc.)
            generated_anchor = re.sub(r"[^a-z0-9\s\-_]", "", generated_anchor)
            # Replace spaces with hyphens
            generated_anchor = re.sub(r"\s+", "-", generated_anchor)
            # Clean up multiple hyphens
            generated_anchor = re.sub(r"-+", "-", generated_anchor)

            if generated_anchor == anchor_name:
                return True

    return False


def main() -> int:  # noqa: C901
    """Main verification function."""
    root = Path(__file__).parent.parent
    print(f"Scanning markdown files in: {root}")
    print()

    # Find all markdown files
    md_files = find_markdown_files(root)
    print(f"Found {len(md_files)} markdown files")
    print()

    # Extract all links
    all_links: list[LinkInfo] = []
    for md_file in md_files:
        links = extract_links(md_file)
        all_links.extend(links)

    print(f"Found {len(all_links)} total links")
    print()

    # Group by type
    internal_links = [link for link in all_links if link["link_type"] == "internal"]
    external_links = [link for link in all_links if link["link_type"] == "external"]
    anchor_links = [link for link in all_links if link["link_type"] == "anchor"]

    print(f"  Internal links: {len(internal_links)}")
    print(f"  External links: {len(external_links)}")
    print(f"  Anchor links: {len(anchor_links)}")
    print()

    # Verify internal links
    print("=" * 80)
    print("VERIFYING INTERNAL LINKS")
    print("=" * 80)
    broken_internal = 0
    for link in internal_links:
        if not verify_internal_link(link["file"], link["target"], root):
            broken_internal += 1
            rel_path = link["file"].relative_to(root)
            print(f"\n❌ BROKEN: {rel_path}:{link['line']}")
            print(f"   Link text: {link['text']}")
            print(f"   Target: {link['target']}")

    if broken_internal == 0:
        print("✅ All internal links are valid!")
    else:
        print(f"\n❌ Found {broken_internal} broken internal links")

    # Verify anchor links
    print()
    print("=" * 80)
    print("VERIFYING ANCHOR LINKS")
    print("=" * 80)
    broken_anchors = 0
    for link in anchor_links:
        if not verify_anchor_link(link["file"], link["target"]):
            broken_anchors += 1
            rel_path = link["file"].relative_to(root)
            print(f"\n❌ BROKEN: {rel_path}:{link['line']}")
            print(f"   Link text: {link['text']}")
            print(f"   Anchor: {link['target']}")

    if broken_anchors == 0:
        print("✅ All anchor links are valid!")
    else:
        print(f"\n❌ Found {broken_anchors} broken anchor links")

    # List external links for manual verification
    print()
    print("=" * 80)
    print("EXTERNAL LINKS (manual verification recommended)")
    print("=" * 80)

    # Group external links by domain
    external_by_domain: dict[str, list[LinkInfo]] = {}
    for link in external_links:
        # Extract domain
        domain_match = re.match(r"https?://([^/]+)", link["target"])
        if domain_match:
            domain = domain_match.group(1)
            if domain not in external_by_domain:
                external_by_domain[domain] = []
            external_by_domain[domain].append(link)

    for domain in sorted(external_by_domain.keys()):
        links = external_by_domain[domain]
        print(f"\n{domain}: {len(links)} links")
        # Show unique URLs
        unique_urls = sorted({link["target"] for link in links})
        for url in unique_urls[:5]:  # Show first 5
            print(f"  - {url}")
        if len(unique_urls) > 5:
            print(f"  ... and {len(unique_urls) - 5} more")

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total markdown files: {len(md_files)}")
    print(f"Total links: {len(all_links)}")
    print(f"  Internal: {len(internal_links)} ({broken_internal} broken)")
    print(f"  External: {len(external_links)} (manual verification needed)")
    print(f"  Anchors: {len(anchor_links)} ({broken_anchors} broken)")
    print()

    if broken_internal > 0 or broken_anchors > 0:
        print("❌ VERIFICATION FAILED - Fix broken links above")
        return 1
    else:
        print("✅ VERIFICATION PASSED - All internal and anchor links valid")
        return 0


if __name__ == "__main__":
    sys.exit(main())
