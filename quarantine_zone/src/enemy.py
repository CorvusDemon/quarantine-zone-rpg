class Enemy:
    def __init__(self, data):
        self.id = data.get("id", "unknown")
        self.name = data.get("name", "Unknown Enemy")
        self.enemy_type = data.get("type", "standard")
        self.is_boss = data.get("is_boss", False)

        self.max_hp = data.get("max_hp", 50)
        self.hp = self.max_hp

        self.base_damage = data.get("base_damage", 10)
        self.infection_on_hit = data.get("infection_on_hit", 0)
        self.attack_pattern = data.get("attack_pattern", "heavy")
        self.escape_chance = data.get("escape_chance", 50)

        self.description = data.get("description", "")
        self.loot_table = data.get("loot_table", [])
        self.no_drop_chance = data.get("no_drop_chance", 50)

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)

    def get_damage(self):
        return self.base_damage