import math
import pygame
from src.settings import *
from src.projectile import Projectile


class Tower:
    """A placed tower on the map — detects enemies in range and fires projectiles."""

    def __init__(self, definition, grid_col, grid_row):
        self.id           = definition["id"]
        self.name         = definition["name"]
        self.cost         = definition["cost"]
        self.col          = grid_col
        self.row          = grid_row

        # Base stats (never mutated — used to recalculate after upgrades)
        self._base_damage      = definition["damage"]
        self._base_firing_rate = definition["firing_rate"]
        self._base_range       = definition["range"]
        self.color             = tuple(definition["color"])
        self.base_crit_chance       = definition.get("crit_chance", 0.0)   # 0.0–1.0
        self.base_dot_damage        = definition.get("dot_damage", 0)       # HP per tick

        # Levels
        self.tower_level    = 1
        self.element_levels = {name: 1 for name in ELEMENT_NAMES}

        # Current effective stats (recalculated on upgrade)
        self.damage      = self._base_damage
        self.firing_rate = self._base_firing_rate
        self.range       = self._base_range
        self.crit_chance = self.base_crit_chance
        self.dot_damage  = self.base_dot_damage

        # Shoot cooldown
        self._cooldown = 0.0

    # ------------------------------------------------------------------
    def _recalculate_stats(self):
        """Recompute effective stats from base + upgrade levels."""
        earth_lvl = self.element_levels["earth"]
        water_lvl = self.element_levels["water"]
        wind_lvl  = self.element_levels["wind"]
        fire_lvl  = self.element_levels["fire"]
        spirit_lvl = self.element_levels["spirit"]

        # Each element contributes (level - 1) worth of bonuses
        self.damage      = self._base_damage      + (earth_lvl - 1) * UPGRADE_DAMAGE_PER_LEVEL
        self.firing_rate = round(self._base_firing_rate + (water_lvl - 1) * UPGRADE_FIRE_RATE_PER_LEVEL, 2)
        self.range       = self._base_range       + (wind_lvl  - 1) * UPGRADE_RANGE_PER_LEVEL
        self.crit_chance = self.base_crit_chance + (spirit_lvl  - 1) * UPGRADE_CRIT_PER_LEVEL
        self.dot_damage  = self.base_dot_damage + (fire_lvl  - 1) * UPGRADE_DOT_PER_LEVEL

    # ------------------------------------------------------------------
    def can_upgrade_element(self, element: str) -> tuple[bool, str]:
        """
        Returns (allowed, reason).
        An element can only be upgraded one level above the tower level.
        """
        current = self.element_levels[element]
        max_allowed = self.tower_level + 1
        if current >= max_allowed:
            return False, f"Upgrade tower first (Lv {self.tower_level})"
        return True, ""

    def upgrade_cost_element(self, element: str) -> int:
        next_level = self.element_levels[element] + 1
        return UPGRADE_COST_BASE * next_level

    def upgrade_element(self, element: str):
        self.element_levels[element] += 1
        self._recalculate_stats()

    # ------------------------------------------------------------------
    def can_upgrade_tower(self) -> tuple[bool, str]:
        """
        Tower level can only increase when ALL element levels equal tower_level + 1.
        """
        required = self.tower_level + 1
        for elem in ELEMENT_NAMES:
            if self.element_levels[elem] < required:
                return False, f"All elements must reach Lv {required}"
        return True, ""

    def upgrade_cost_tower(self) -> int:
        next_level = self.tower_level + 1
        return TOWER_LEVELUP_COST * next_level

    def upgrade_tower(self):
        self.tower_level += 1
        self._recalculate_stats()

    # ------------------------------------------------------------------
    @property
    def rect(self):
        return pygame.Rect(self.col * TILE_SIZE, self.row * TILE_SIZE,
                           TILE_SIZE, TILE_SIZE)

    @property
    def centre(self):
        return (self.col * TILE_SIZE + TILE_SIZE // 2,
                self.row * TILE_SIZE + TILE_SIZE // 2)

    @property
    def range_px(self):
        return self.range * TILE_SIZE

    # ------------------------------------------------------------------
    def update(self, dt: float, enemies: list) -> list:
        new_projectiles = []
        if self.firing_rate <= 0:
            return new_projectiles
        self._cooldown -= dt
        if self._cooldown > 0:
            return new_projectiles
        target = self._pick_target(enemies)
        if target is None:
            return new_projectiles
        import random
        # Determine if this shot crits
        is_crit   = random.random() < self.crit_chance
        final_dmg = self.damage * 2 if is_crit else self.damage

        cx, cy = self.centre
        new_projectiles.append(
            Projectile(float(cx), float(cy), target, final_dmg, self.color,
                       is_crit=is_crit,
                       dot_damage=self.dot_damage)
        )
        self._cooldown = 1.0 / self.firing_rate
        return new_projectiles

    def _pick_target(self, enemies):
        cx, cy = self.centre
        best   = None
        for enemy in enemies:
            if enemy.dead or enemy.reached_end:
                continue
            dist = math.hypot(enemy.x - cx, enemy.y - cy)
            if dist > self.range_px:
                continue
            if best is None or enemy.waypoint_idx > best.waypoint_idx:
                best = enemy
        return best

    # ------------------------------------------------------------------
    def draw(self, surface):
        r = self.rect
        pygame.draw.rect(surface, self.color, r)
        pygame.draw.rect(surface, BLACK, r, 2)
        inner  = r.inflate(-18, -18)
        darker = tuple(max(0, c - 50) for c in self.color)
        pygame.draw.rect(surface, darker, inner)

        # Tower level badge — top-right corner
        cx, cy = self.centre
        lv_surf = pygame.font.SysFont("monospace", 11, bold=True).render(
            f"Lv{self.tower_level}", True, GOLD)
        surface.blit(lv_surf, (r.right - lv_surf.get_width() - 3, r.top + 2))

        # Cannon dot
        pygame.draw.circle(surface, BLACK, (cx, cy), 5)
        pygame.draw.circle(surface, self.color, (cx, cy), 4)

