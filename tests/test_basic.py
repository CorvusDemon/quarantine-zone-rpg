import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def test_player_creation():
    from src.player import Player
    p = Player(name="Test", start_location_id="police_station")
    assert p.hp == 100
    assert p.infection == 0
    assert p.current_location_id == "police_station"
    print("[OK] test_player_creation")


def test_enemy_creation():
    from src.enemy import Enemy
    data = {
        "id": "test_zombie",
        "name": "Test Zombie",
        "type": "standard",
        "is_boss": False,
        "max_hp": 60,
        "base_damage": 18,
        "infection_on_hit": 3,
        "attack_pattern": "heavy",
        "escape_chance": 70,
        "loot_table": [],
        "no_drop_chance": 35
    }
    e = Enemy(data)
    assert e.hp == 60
    assert e.is_alive() is True
    e.take_damage(999)
    assert e.is_alive() is False
    print("[OK] test_enemy_creation")


def test_save_manager():
    from src.save_manager import SaveManager
    from src.player import Player
    import tempfile

    sm = SaveManager()
    with tempfile.TemporaryDirectory() as tmpdir:
        save_path = Path(tmpdir) / "save_test.json"

        p = Player("Test", "police_station")
        p.add_item("bandage", 1)
        p.add_infection(10)
        p.take_damage(20)         

        result = sm.save_game(p, None, save_path)
        assert result is True

        p2 = Player("Test2", "street")
        _, ok = sm.load_game(p2, {}, save_path)
        assert ok is True
        assert p2.hp == 80      
        assert p2.infection == 10

        p_restored = Player("Fresh", "police_station")
        _, ok_final = sm.load_game(p_restored, {}, save_path)
        assert ok_final is True
        assert p_restored.hp == 80         
        assert p_restored.infection == 10
        print("[OK] test_save_manager")


def test_data_integrity():
    from pathlib import Path
    DATA_DIR = Path(__file__).resolve().parent.parent / "data"

    required_files = {
        "items.json": ["items"],
        "enemies.json": ["enemies"],
        "locations.json": ["locations"],
        "recipes.json": ["recipes"],
        "notes.json": ["notes"]
    }

    for filename, required_keys in required_files.items():
        path = DATA_DIR / filename
        if not path.exists():
            print(f"[WARN] Missing file: {filename}")
            continue

        import json
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for key in required_keys:
            if key not in data:
                print(f"[ERROR] {filename} missing key: {key}")
                assert False, f"{filename} missing key: {key}" 

    print("[OK] test_data_integrity")


if __name__ == "__main__":
    test_player_creation()
    test_enemy_creation()
    test_save_manager()
    test_data_integrity()