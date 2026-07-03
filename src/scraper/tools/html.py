import json
import re
import sys
import uuid
from datetime import date
from pathlib import Path
from bs4 import BeautifulSoup

# repo root added so CDP_script.py (at root) is importable from here
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from CDP_script import connect, fetch_html
from src.scraper.url_builder.builder import catalog_url as build_catalog_url

class HTMLTools:
    COVERAGE_HEAD_SIZE = 20

    def __init__(self, brand: str):
        self.brand = brand
        self.batch_id: str | None = None
        self.config = self.set_scrape_config(brand)
        self.soup = None

    def set_scrape_config(self, brand: str) -> dict:
        config_path = Path(__file__).parent.parent / "dom_config.json"
        with open(config_path) as f:
            config = json.load(f)

        default = config.get("default", {})
        brand_override = config.get(brand, {})

        merged = {
            "json_ld": {**default.get("json_ld", {}), **brand_override.get("json_ld", {})},
            "dom": {
                **default.get("dom", {}),
                "fields": {
                    **default.get("dom", {}).get("fields", {}),
                    **brand_override.get("dom", {}).get("fields", {}),
                }
            }
        }
        return merged

    def load_html(self, html_path: str):
        self.soup = BeautifulSoup(Path(html_path).read_text(encoding="utf-8"), "lxml")

    async def generate_catalog_html(self, brand: str) -> str:
        url = build_catalog_url(brand)
        browser = await connect()
        if not browser:
            raise RuntimeError("Could not connect to Chrome (port 9222).")
        try:
            html = await fetch_html(url, browser)
        finally:
            await browser.close()

        batch_id = uuid.uuid4().hex[:5]
        date_str = date.today().strftime("%m%d%y")
        out_dir = _REPO_ROOT / "db" / "html" / "catalog" / brand
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{date_str}_{batch_id}.html"
        out_path.write_text(html, encoding="utf-8")
        print(f"[+] Saved {len(html):,} bytes -> {out_path}")
        return batch_id

    def check_catalog_html(self, brand: str, batch_id: str) -> bool:
        catalog_dir = Path(__file__).parent.parent.parent.parent / "db" / "html" / "catalog" / brand
        if not catalog_dir.exists():
            return False
        return any(f.stem.endswith(f"_{batch_id}") for f in catalog_dir.iterdir())

    def get_catalog_html_path(self, brand: str, batch_id: str) -> Path | None:
        catalog_dir = Path(__file__).parent.parent.parent.parent / "db" / "html" / "catalog" / brand
        if not catalog_dir.exists():
            return None
        return next((f for f in catalog_dir.iterdir() if f.stem.endswith(f"_{batch_id}")), None)

    def clean_catalog_html(self, brand: str, batch_id: str) -> list:
        """Parse the saved catalog HTML for this brand+batch_id into a list of listing dicts."""
        path = self.get_catalog_html_path(brand, batch_id)
        if path is None:
            raise FileNotFoundError(f"No catalog HTML for {brand}/{batch_id}")
        self.load_html(str(path))

        cfg = self.config
        json_ld_cfg = cfg["json_ld"]
        raw = self.get_json_ld_fields(json_ld_cfg["listings_path"]) or []
        field_map = json_ld_cfg.get("fields", {})

        card_pattern = re.compile(cfg["dom"]["card_testid"])
        cards = self.soup.find_all("div", {"data-testid": card_pattern})

        # config field name -> output dict key (everything else maps 1:1)
        key_alias = {"price_original": "price", "price_final": "final_price"}

        listings = []
        for i, card in enumerate(cards):
            meta = raw[i] if i < len(raw) else {}
            row = {
                "name": meta.get(field_map.get("name", "name")),
                "brand": brand,
                "listing_url": meta.get(field_map.get("listing_url", "url")),
                "image_url": meta.get(field_map.get("image_url", "image")),
            }
            for cfg_field, testid_suffix in cfg["dom"].get("fields", {}).items():
                el = card.find(attrs={"data-testid": re.compile(testid_suffix + "$")})
                value = el.get_text(strip=True) if el else None
                row[key_alias.get(cfg_field, cfg_field)] = value
            listings.append(row)

        return listings

    ## AGENT TOOLS GO PAST HERE ##

    ALLOWED_FIELDS = ("size", "price_original", "price_final", "price_callout")

    # Field name in scrape_config -> output-dict key produced by clean_catalog_html.
    _CFG_TO_OUTPUT = {"price_original": "price", "price_final": "final_price"}

    def try_field_suffixes(self, candidates: dict) -> dict:
        """Test multiple candidate testid_suffixes per field in isolation.

        `candidates` maps field name -> list of candidate suffixes to try, e.g.
            {"price_final": ["-sale-price", "-price-final", "-discount"],
             "price_original": ["-price-original"]}
        For each (field, suffix) pair, only that field is patched; other
        fields keep their current suffix. Suffixes are deduped per field.
        Duplicate-suffix guard runs on the price fields: if a candidate
        yields listings where price == final_price on every populated row,
        that candidate's coverage is reported as 0 with a note.

        Returns:
            {"results": {field: {"best": {"suffix": s, "coverage": p},
                                  "ranked": [{"suffix": s, "coverage": p, "note": str|None}, ...]}}}
        Restores self.config on exit.
        """
        if self.batch_id is None:
            raise RuntimeError("try_field_suffixes called before batch_id was bound")
        if not candidates:
            raise ValueError("candidates cannot be empty")
        for field in candidates:
            if field not in self.ALLOWED_FIELDS:
                raise ValueError(f"unknown field {field!r}; allowed: {self.ALLOWED_FIELDS}")

        old_config = self.config
        results: dict = {}
        try:
            for field, suffix_list in candidates.items():
                seen = set()
                unique_suffixes = [s for s in suffix_list if not (s in seen or seen.add(s))]
                out_key = self._CFG_TO_OUTPUT.get(field, field)
                ranked = []

                for suffix in unique_suffixes:
                    self.config = {
                        **old_config,
                        "dom": {
                            **old_config["dom"],
                            "fields": {**old_config["dom"].get("fields", {}), field: suffix},
                        },
                    }
                    listings = self.clean_catalog_html(self.brand, self.batch_id)
                    head = listings[: self.COVERAGE_HEAD_SIZE]
                    total = len(head)
                    coverage = (
                        sum(1 for l in head if l.get(out_key)) / total if total else 0.0
                    )

                    note = None
                    if field in ("price_original", "price_final") and coverage > 0:
                        pairs = [(l["price"], l["final_price"]) for l in head
                                 if l.get("price") and l.get("final_price")]
                        if pairs and all(p == f for p, f in pairs):
                            other = "price_final" if field == "price_original" else "price_original"
                            note = f"duplicate of {other} — suffixes resolve to the same DOM node"
                            coverage = 0.0

                    ranked.append({"suffix": suffix, "coverage": coverage, "note": note})

                ranked.sort(key=lambda r: r["coverage"], reverse=True)
                best = {"suffix": ranked[0]["suffix"], "coverage": ranked[0]["coverage"]} if ranked else None
                results[field] = {"best": best, "ranked": ranked}

            return {"results": results}
        finally:
            self.config = old_config

    def get_json_ld(self) -> dict:
        script = self.soup.find("script", {"type": "application/ld+json"})
        if not script:
            return {}
        return json.loads(script.string)

    def get_json_ld_fields(self, path: list[str]) -> any:
        data = self.get_json_ld()
        for key in path:
            if isinstance(data, list):
                data = data[int(key)]
            else:
                data = data.get(key)
            if data is None:
                return None
        return data

    def get_card_testids(
        self,
        keyword: str | None = None,
        card_limit: int = 10,
        limit: int = 10,
    ) -> list[dict]:
        cards = self.soup.find_all("div", {"data-testid": re.compile(r"^plp-product/\d+$")})
        if not cards:
            return []
        counts: dict[str, int] = {}
        first_seen: dict[str, int] = {}
        for i, card in enumerate(cards[:card_limit]):
            # per-card set: each testid counts once per card, not per element
            card_testids = {el["data-testid"] for el in card.find_all(attrs={"data-testid": True})}
            for tid in card_testids:
                if keyword and keyword not in tid:
                    continue
                if tid not in counts:
                    first_seen[tid] = i
                    counts[tid] = 0
                counts[tid] += 1
        ordered = sorted(counts.keys(), key=lambda t: (-counts[t], first_seen[t]))
        return [{"testid": t, "count": counts[t]} for t in ordered[:limit]]

    def get_element_context(
        self,
        testid_suffix: str,
        chars: int = 40,
        card_limit: int = 10,
        limit: int = 10,
    ) -> list[str]:
        cards = self.soup.find_all("div", {"data-testid": re.compile(r"^plp-product/\d+$")})
        if not cards:
            return []

        pattern = re.compile(r'data-testid="[^"]*' + re.escape(testid_suffix) + r'"')
        results: list[str] = []

        for card in cards[:card_limit]:
            card_html = str(card)
            for match in pattern.finditer(card_html):
                start = max(0, match.start() - chars)
                end = min(len(card_html), match.end() + chars)
                results.append(card_html[start:end])
                if len(results) >= limit:
                    return results

        return results

""" DOM_CONFIG.JSON SHAPE FOR SELECTOR PREFERENCES, where "default" becomes the brand name like "undercover"
 {                                                                                                                
    "default": {                                                                                                   
      "json_ld": {                                                                                                 
        "script_type": "application/ld+json",                                                                      
        "listings_path": ["mainEntity", "itemListElement"],
        "fields": {                                                                                                
          "name": "name",                                                                                          
          "listing_url": "url",
          "image_url": "image"                                                                                     
        }                                                                                                        
      },                                                                                                           
      "dom": {                                                                                                   
        "card_testid": "^plp-product/\\d+$",                                                                       
        "fields": {                           
          "size": "-size",                                                                                         
          "price_original": "-price-original",                                                                   
          "price_final": "-price-final",                                                                           
          "price_callout": "-price-callout"
        }                                                                                                          
      }                                                                                                            
    }
    """