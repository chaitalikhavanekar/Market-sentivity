"""
SECTOR IMPACT MODEL
Maps macro shock scenarios to sector-level market impact.
"""


class SectorImpactModel:
    """
    Provides sector-level impact ratings for each shock scenario.
    Impact scale: -3 (severe negative) to +3 (severe positive), 0 = neutral
    """

    SECTOR_IMPACTS: dict[str, dict[str, int]] = {

        "WAR": {
            "Energy":        +3,
            "Defense":       +3,
            "Gold Mining":   +2,
            "Aerospace":     +2,
            "Agriculture":   +1,
            "Utilities":     +1,
            "Financials":    -1,
            "Technology":    -1,
            "Consumer Disc": -2,
            "Airlines":      -3,
            "Tourism":       -3,
            "Shipping":      -2,
        },

        "RATE_HIKE": {
            "Banking":       +2,
            "Insurance":     +2,
            "Financials":    +1,
            "Commodities":   +0,
            "Healthcare":    -1,
            "Consumer Disc": -1,
            "Utilities":     -2,
            "Real Estate":   -3,
            "Technology":    -2,
            "Biotech":       -2,
            "Growth Stocks": -3,
        },

        "OIL_SHOCK": {
            "Oil & Gas":     +3,
            "Energy":        +3,
            "Oil Services":  +2,
            "Pipelines":     +1,
            "Mining":        +1,
            "Consumer Disc": -1,
            "Chemicals":     -1,
            "Transportation":-2,
            "Airlines":      -3,
            "Shipping":      -2,
            "Plastics":      -2,
        },

        "PANDEMIC": {
            "Biotech":       +3,
            "Pharma":        +3,
            "E-Commerce":    +2,
            "Digital Media": +2,
            "Telecom":       +1,
            "Utilities":     +1,
            "Energy":        -2,
            "Retail":        -2,
            "Hospitality":   -3,
            "Airlines":      -3,
            "Tourism":       -3,
            "Commercial RE": -2,
        },

        "CURRENCY_CRISIS": {
            "Export-Heavy":  +2,
            "Gold Mining":   +2,
            "Commodities":   +1,
            "Crypto":        +1,
            "Staples":       -1,
            "Financials":    -2,
            "Importers":     -2,
            "Retail":        -2,
            "EM Bonds":      -3,
            "EM Equities":   -3,
        },

        "NONE": {
            "Technology":    +1,
            "Healthcare":    +1,
            "Consumer Disc": +1,
            "Financials":    +0,
            "Energy":        +0,
            "Utilities":     -0,
            "Real Estate":   +0,
            "Industrials":   +1,
        },
    }

    def get_impact(self, scenario: str) -> dict[str, int]:
        """Return sector impact map for a given scenario."""
        return self.SECTOR_IMPACTS.get(scenario, self.SECTOR_IMPACTS["NONE"])

    def get_winners(self, scenario: str, top_n: int = 3) -> list[tuple[str, int]]:
        """Return top N positively impacted sectors."""
        impacts = self.get_impact(scenario)
        return sorted(
            [(s, v) for s, v in impacts.items() if v > 0],
            key=lambda x: x[1], reverse=True
        )[:top_n]

    def get_losers(self, scenario: str, top_n: int = 3) -> list[tuple[str, int]]:
        """Return top N negatively impacted sectors."""
        impacts = self.get_impact(scenario)
        return sorted(
            [(s, v) for s, v in impacts.items() if v < 0],
            key=lambda x: x[1]
        )[:top_n]
