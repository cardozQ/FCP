"""Content extraction helpers."""

from __future__ import annotations

from typing import List

from bs4 import BeautifulSoup
from readability import Document

from .utils import MAX_CONTENT_CHARS, chunk_text, normalize_text, truncate_text

NOISE_TAGS = ("script", "style", "nav", "aside", "footer", "noscript", "form")
NOISE_PATTERNS = (
    "ad",
    "ads",
    "advert",
    "banner",
    "cookie",
    "promo",
    "popup",
    "sidebar",
    "subscribe",
)


class Extractor:
    def extract(self, html: str) -> dict:
        if not html:
            return {
                "title": "",
                "headings": [],
                "content": "",
                "code_blocks": [],
                "sections": [],
                "chunks": [],
                "truncated": False,
                "content_chars": 0,
            }

        document = Document(html)
        summary_html = document.summary()
        title = document.short_title() or ""

        soup = BeautifulSoup(summary_html, "html.parser")
        fallback_soup = BeautifulSoup(html, "html.parser")

        self._clean_soup(soup)
        self._clean_soup(fallback_soup)
        self._remove_noise_blocks(soup)
        self._remove_noise_blocks(fallback_soup)

        extraction_root = self._pick_extraction_root(soup, fallback_soup)

        headings = [
            heading.get_text(" ", strip=True)
            for heading in extraction_root.find_all(["h1", "h2", "h3"])
            if heading.get_text(" ", strip=True)
        ]
        code_blocks = [
            code.get_text("\n", strip=True)
            for code in extraction_root.find_all(["pre", "code"])
            if code.get_text(" ", strip=True)
        ]
        sections = self._extract_sections(extraction_root)
        content = normalize_text(
            "\n\n".join(
                section["content"] for section in sections if section["content"]
            )
        )
        content, truncated = truncate_text(content, MAX_CONTENT_CHARS)
        chunks = chunk_text(content)
        deduped_code_blocks = self._dedupe(code_blocks)

        return {
            "title": title,
            "headings": self._dedupe(headings),
            "content": content,
            "code_blocks": deduped_code_blocks,
            "sections": sections,
            "chunks": chunks,
            "truncated": truncated,
            "content_chars": len(content),
        }

    def _clean_soup(self, soup: BeautifulSoup) -> None:
        for tag_name in NOISE_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()

    def _pick_extraction_root(
        self, summary_soup: BeautifulSoup, fallback_soup: BeautifulSoup
    ) -> BeautifulSoup:
        summary_sections = self._extract_sections(summary_soup)
        summary_text = normalize_text(
            "\n\n".join(
                section["content"] for section in summary_sections if section["content"]
            )
        )
        if summary_text:
            return summary_soup

        fallback_root = (
            fallback_soup.find("article")
            or fallback_soup.find("main")
            or fallback_soup.body
            or fallback_soup
        )
        return BeautifulSoup(str(fallback_root), "html.parser")

    def _remove_noise_blocks(self, soup: BeautifulSoup) -> None:
        for tag in soup.find_all(True):
            attrs_dict = tag.attrs or {}
            attrs = " ".join(
                part
                for part in (
                    attrs_dict.get("id", ""),
                    " ".join(attrs_dict.get("class", [])),
                    attrs_dict.get("role", ""),
                    attrs_dict.get("aria-label", ""),
                )
                if part
            ).lower()
            if attrs and any(pattern in attrs for pattern in NOISE_PATTERNS):
                tag.decompose()

    def _extract_sections(self, soup: BeautifulSoup) -> List[dict]:
        sections: List[dict] = []
        current_title = "Introduction"
        current_parts: List[str] = []

        def flush_section() -> None:
            nonlocal current_parts
            content = normalize_text("\n".join(current_parts))
            if content:
                section_content, _ = truncate_text(content, 2000)
                sections.append({"title": current_title, "content": section_content})
            current_parts = []

        for tag in soup.find_all(["h1", "h2", "h3", "p", "li", "pre", "blockquote"]):
            text = tag.get_text("\n", strip=True)
            if not text:
                continue

            if tag.name in {"h1", "h2", "h3"}:
                flush_section()
                current_title = text
                continue

            current_parts.append(text)

        flush_section()
        return sections

    def _dedupe(self, items: List[str]) -> List[str]:
        seen: set[str] = set()
        deduped: List[str] = []

        for item in items:
            normalized = normalize_text(item)
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            deduped.append(normalized)

        return deduped
