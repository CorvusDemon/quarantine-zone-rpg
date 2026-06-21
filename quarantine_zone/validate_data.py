import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

ERRORS = []
WARNINGS = []


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        ERRORS.append(f"[FILE NOT FOUND] {path}")
        return {}
    except json.JSONDecodeError as e:
        ERRORS.append(f"[JSON ERROR] {path}: {e}")
        return {}


def validate():
    # Load all data
    items_data     = load_json(DATA_DIR / "items.json")
    recipes_data   = load_json(DATA_DIR / "recipes.json")
    enemies_data   = load_json(DATA_DIR / "enemies.json")
    locations_data = load_json(DATA_DIR / "locations.json")
    notes_data     = load_json(DATA_DIR / "notes.json")

    items     = {i["id"]: i for i in items_data.get("items", [])}
    enemies   = {e["id"]: e for e in enemies_data.get("enemies", [])}
    locations = {location["id"]: location for location in locations_data.get("locations", [])}
    recipes   = recipes_data.get("recipes", [])
    notes     = notes_data.get("notes", [])

    print(f"Loaded: {len(items)} items, {len(enemies)} enemies, "
          f"{len(locations)} locations, {len(recipes)} recipes, "
          f"{len(notes)} notes\n")

    # ── Validate recipes ──────────────────────────────────────
    print("Checking recipes...")
    for recipe in recipes:
        rid = recipe.get("id", "?")

        # Materials exist
        for mat in recipe.get("materials", []):
            iid = mat.get("item_id")
            if iid not in items:
                ERRORS.append(
                    f"[RECIPE] '{rid}' requires unknown item '{iid}'"
                )

        # Result exists
        result_id = recipe.get("result", {}).get("item_id")
        if result_id not in items:
            ERRORS.append(
                f"[RECIPE] '{rid}' produces unknown item '{result_id}'"
            )

        # unlocked_by flag
        unlocked_by = recipe.get("unlocked_by", "default")
        if unlocked_by not in ("default",
                               "first_aid_notes",
                               "research_notes",
                               "lab_formula"):
            WARNINGS.append(
                f"[RECIPE] '{rid}' unlocked_by unknown flag '{unlocked_by}'"
            )

    # ── Validate locations ────────────────────────────────────
    print("Checking locations...")
    for loc_id, loc in locations.items():

        # Connections point to existing locations
        for conn in loc.get("connections", []):
            tid = conn.get("target_id")
            if tid not in locations:
                ERRORS.append(
                    f"[LOCATION] '{loc_id}' connection to unknown '{tid}'"
                )

            # Requirements reference existing items
            for req in conn.get("requirements", []):
                if req.get("type") == "item":
                    if req.get("id") not in items:
                        ERRORS.append(
                            f"[LOCATION] '{loc_id}' connection requires "
                            f"unknown item '{req.get('id')}'"
                        )

        # Loot table items exist
        for entry in loc.get("search_loot_table", []):
            iid = entry.get("item_id")
            if iid not in items:
                ERRORS.append(
                    f"[LOCATION] '{loc_id}' loot table has unknown item '{iid}'"
                )

        # Encounter table enemies exist
        for entry in loc.get("encounter_table", []):
            eid = entry.get("enemy_id")
            if eid not in enemies:
                ERRORS.append(
                    f"[LOCATION] '{loc_id}' encounter table has "
                    f"unknown enemy '{eid}'"
                )

        # Special actions
        for action in loc.get("special_actions", []):
            aid = action.get("id", "?")

            # Reward items exist
            for entry in action.get("rewards", {}).get("items", []):
                iid = entry.get("item_id")
                if iid not in items:
                    ERRORS.append(
                        f"[ACTION] '{loc_id}/{aid}' rewards unknown item '{iid}'"
                    )

            # Boss battle enemy exists
            if action.get("type") == "boss_battle":
                eid = action.get("enemy_id")
                if eid not in enemies:
                    ERRORS.append(
                        f"[ACTION] '{loc_id}/{aid}' boss_battle "
                        f"unknown enemy '{eid}'"
                    )

            # Note rewards exist
            for note_id in action.get("rewards", {}).get("notes", []):
                note_ids = {n["id"] for n in notes}
                if note_id not in note_ids:
                    WARNINGS.append(
                        f"[ACTION] '{loc_id}/{aid}' rewards unknown "
                        f"note '{note_id}'"
                    )

        # Protection item exists
        prot = loc.get("protection_item_id")
        if prot and prot not in items:
            ERRORS.append(
                f"[LOCATION] '{loc_id}' protection_item_id "
                f"unknown item '{prot}'"
            )

        # Map coordinates present
        if "map_x" not in loc or "map_y" not in loc:
            WARNINGS.append(
                f"[LOCATION] '{loc_id}' missing map_x / map_y"
            )

    # ── Validate enemies ──────────────────────────────────────
    print("Checking enemies...")
    for eid, enemy in enemies.items():

        # Loot table items exist
        for entry in enemy.get("loot_table", []):
            iid = entry.get("item_id")
            if iid not in items:
                ERRORS.append(
                    f"[ENEMY] '{eid}' loot table has unknown item '{iid}'"
                )

        # attack_pattern valid
        valid_patterns = {"heavy", "fast", "toxic", "mixed"}
        pat = enemy.get("attack_pattern")
        if pat not in valid_patterns:
            ERRORS.append(
                f"[ENEMY] '{eid}' unknown attack_pattern '{pat}'"
            )

    # ── Validate notes ────────────────────────────────────────
    print("Checking notes...")
    note_ids = set()
    for note in notes:
        nid = note.get("id", "?")

        # Duplicate IDs
        if nid in note_ids:
            ERRORS.append(f"[NOTE] Duplicate note id '{nid}'")
        note_ids.add(nid)

        # found_in points to existing location
        found_in = note.get("found_in")
        if found_in and found_in not in locations:
            WARNINGS.append(
                f"[NOTE] '{nid}' found_in unknown location '{found_in}'"
            )

        # Required fields
        for field in ("title", "text"):
            if not note.get(field):
                WARNINGS.append(f"[NOTE] '{nid}' missing field '{field}'")

    # ── Results ───────────────────────────────────────────────
    print("\n" + "=" * 50)

    if ERRORS:
        print(f"❌ ERRORS ({len(ERRORS)}):")
        for e in ERRORS:
            print(f"   {e}")
    else:
        print("✅ No errors found.")

    if WARNINGS:
        print(f"\n⚠️  WARNINGS ({len(WARNINGS)}):")
        for w in WARNINGS:
            print(f"   {w}")
    else:
        print("✅ No warnings.")

    print("=" * 50)
    print(f"\nResult: {len(ERRORS)} error(s), {len(WARNINGS)} warning(s)")

    return len(ERRORS) == 0


if __name__ == "__main__":
    ok = validate()
    exit(0 if ok else 1)