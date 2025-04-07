keyword_categories = [
    "natural sciences", "water and technology", "social sciences"
]

with open("hierarchy.txt", "r") as f:
    keyword_dict = {}
    lines = f.readlines()
    current_head = []
    for line in lines:
        current_category = [cat for cat in keyword_categories if cat in line]
        if current_category:
            category = current_category
            level = 1
            assert len(category) == 1
            category = category[0]
        else:
            indentation = 0
            for c in line:
                indentation += 1 if c == " " or not c.isascii() else 0
                if c.isalpha():
                    break
            # Highest indentation signifies keyword
            if indentation == 16:
                keyword = "".join(c for c in line if ord(c) < 128).strip()
                keyword_dict[keyword] = category

print(keyword_dict)
