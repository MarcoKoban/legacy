#!/usr/bin/env python3
"""
Update coverage badge in root README.md
"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path


def get_coverage_percentage(coverage_xml_path: Path) -> float:
    """Extract coverage percentage from coverage.xml"""
    try:
        tree = ET.parse(coverage_xml_path)
        root = tree.getroot()

        # Get coverage from the root element
        coverage = root.attrib.get("line-rate", "0")
        percentage = float(coverage) * 100
        return round(percentage, 1)
    except Exception as e:
        print(f"Warning: Could not parse coverage.xml: {e}")
        return 0.0


def get_badge_color(coverage: float) -> str:
    """Get badge color based on coverage percentage"""
    if coverage >= 90:
        return "brightgreen"
    elif coverage >= 75:
        return "green"
    elif coverage >= 60:
        return "yellow"
    elif coverage >= 40:
        return "orange"
    else:
        return "red"


def create_coverage_badge(coverage: float) -> str:
    """Create coverage badge markdown"""
    color = get_badge_color(coverage)
    badge_url = f"https://img.shields.io/badge/Coverage-{coverage:.1f}%25-{color}.svg"
    badge_link = "geneweb_python/htmlcov/index.html"
    return f"[![Coverage]({badge_url})]({badge_link})"


def update_readme(readme_path: Path, coverage_badge: str):
    """Update README.md with coverage badge"""
    content = readme_path.read_text(encoding="utf-8")

    # Pattern to find existing coverage badge
    coverage_pattern = (
        r"\[!\[Coverage\]\(https://img\.shields\.io/badge/Coverage-[^\)]+\)\]\([^\)]+\)"
    )

    if re.search(coverage_pattern, content):
        # Replace existing badge
        new_content = re.sub(coverage_pattern, coverage_badge, content)
        print("✅ Updated existing coverage badge")
    else:
        # Add badge after the License badge
        license_pattern = r"(\[!\[License\][^\]]+\][^\n]+)"
        new_content = re.sub(license_pattern, f"\\1\n{coverage_badge}", content)
        print("✅ Added new coverage badge")

    readme_path.write_text(new_content, encoding="utf-8")


def main():
    """Main function"""
    # Paths
    project_root = Path(__file__).parent.parent.parent
    coverage_xml = project_root / "geneweb_python" / "coverage.xml"
    readme = project_root / "README.md"

    print(f"📊 Reading coverage from: {coverage_xml}")

    if not coverage_xml.exists():
        print("❌ coverage.xml not found. Run tests first: make test")
        return 1

    if not readme.exists():
        print("❌ README.md not found")
        return 1

    # Get coverage
    coverage = get_coverage_percentage(coverage_xml)
    print(f"📈 Coverage: {coverage:.1f}%")

    # Create and update badge
    badge = create_coverage_badge(coverage)
    print(f"🎨 Badge: {badge}")

    update_readme(readme, badge)
    print(f"✅ Updated {readme}")

    return 0


if __name__ == "__main__":
    exit(main())
