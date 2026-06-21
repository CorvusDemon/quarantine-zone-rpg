class Player:
    def __init__(self, name, start_location_id):
        self.name = name

        self.max_hp = 100
        self.hp = 100

        self.infection = 0
        self.max_infection = 100

        self.current_location_id = start_location_id
        self.found_notes = []  # list of note ids in order found
        self.visited_locations = {start_location_id}

        self.inventory = {}
        self.flags = {
            "first_aid_notes": False,
            "research_notes": False,
            "lab_formula": False,
        }

        self.suppressant_battles_left = 0
        self.used_one_time_actions = set()

        self.escape_attempts = 0

    def is_alive(self):
        return self.hp > 0 and self.infection < self.max_infection

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)

    def heal(self, amount):
        effective_amount = amount
        if self.infection >= 50:
            effective_amount = int(amount * 0.8)
        self.hp = min(self.max_hp, self.hp + effective_amount)

    def add_infection(self, amount):
        if self.suppressant_battles_left > 0:
            amount = int(amount * 0.5)
        self.infection = min(self.max_infection, self.infection + amount)

    def reduce_infection(self, amount):
        self.infection = max(0, self.infection - amount)

    def add_item(self, item_id, quantity=1):
        if item_id in self.inventory:
            self.inventory[item_id] += quantity
        else:
            self.inventory[item_id] = quantity

    def remove_item(self, item_id, quantity=1):
        if item_id not in self.inventory:
            return False
        if self.inventory[item_id] < quantity:
            return False
        self.inventory[item_id] -= quantity
        if self.inventory[item_id] <= 0:
            del self.inventory[item_id]
        return True

    def has_item(self, item_id, quantity=1):
        return item_id in self.inventory and self.inventory[item_id] >= quantity

    def get_infection_state(self):
        if self.infection >= 100:
            return "Transformation"
        if self.infection >= 75:
            return "Critical"
        if self.infection >= 50:
            return "Instability"
        if self.infection >= 25:
            return "Fever"
        return "Stable"