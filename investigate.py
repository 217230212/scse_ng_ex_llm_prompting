import json

from parse_data import load_items, get_unclaimed_items, save_result


def build_prompt(description, available_items):
    system_prompt = """You are a campus lost-and-found assistant. 
Your job is to match a user's description of a lost item to items in the lost-and-found database.

Rules:
- You must use only the given JSON data of available items.
- Not all details of an item must match to be a possible match.
- You must return ONLY valid JSON with exactly the following structure:
{
    "matches": ["ITEM_ID"],
    "confidence": "LOW"
}

- "matches" contains all the possible match IDs.
- "confidence" measures how confident you are about the matches.
- "confidence" must be exactly one of: LOW, MEDIUM, HIGH.
- If there is no match, return an empty list for "matches".
- Do not include any text outside the JSON."""

    user_prompt = f"""Available items in the lost-and-found database:
{json.dumps(available_items, indent=2)}

User's description of the lost item:
{description}

Find all possible matches from the database. Return only JSON."""

    return system_prompt, user_prompt


def ask_qwen(system_prompt, user_prompt):
    import ollama
    response = ollama.chat(
        model="qwen2.5",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response["message"]["content"]


def parse_response(response_text):
    response_text = response_text.strip()
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        lines = lines[1:-1]
        response_text = "\n".join(lines)
    return json.loads(response_text)


def validate_result(result, available_items):
    if not isinstance(result, dict):
        return False
    if "matches" not in result or "confidence" not in result:
        return False
    if not isinstance(result["matches"], list):
        return False
    if result["confidence"] not in ("LOW", "MEDIUM", "HIGH"):
        return False
    valid_ids = {item["id"] for item in available_items}
    for match_id in result["matches"]:
        if match_id not in valid_ids:
            return False
    return True


def display_matches(result, available_items):
    matches = result["matches"]
    confidence = result["confidence"]

    print("\nMATCH RESULT")
    print("-" * 50)
    print(f"Confidence: {confidence}")

    if not matches:
        print("\nNo matches found.")
        print(f"Matches: {matches}")
    else:
        print("\nPossible matches:")
        for match_id in matches:
            for item in available_items:
                if item["id"] == match_id:
                    print()
                    print(f"ID: {item['id']}")
                    print(f"Item: {item['item']}")
                    print(f"Color: {item['color']}")
                    print(f"Location: {item['location']}")
                    print(f"Date found: {item['date']}")
                    break


def main():
    items = load_items("found_items.json")
    available_items = get_unclaimed_items(items)

    print("CAMPUS LOST-AND-FOUND ASSISTANT")
    print("=" * 50)
    print()

    description = input("Describe the item you lost: ")
    print()
    print("Searching for possible matches...")

    system_prompt, user_prompt = build_prompt(description, available_items)
    response_text = ask_qwen(system_prompt, user_prompt)
    result = parse_response(response_text)

    if not validate_result(result, available_items):
        print("Error: Invalid response from the model.")
        return

    display_matches(result, available_items)

    save_result(result, "output/match_result.json")
    print("\nResult saved to output/match_result.json")


if __name__ == "__main__":
    main()
