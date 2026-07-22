
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "hierarchy-social-media.txt")

keyword_categories = [
    "natural sciences", "water and technology", "social sciences"
]


def get_keyword_variations(keywords):
    keywords = keywords.lower()
    if "*" in keywords:
        keyword_list = [
            keywords.replace("*", ""),
            keywords.replace("*", "-"),
            keywords.replace("*", " ")
        ]
    elif "/" in keywords:
        split = keywords.split("/")
        fst = split[0]
        snd_split = split[1].strip().split(" ")
        snd = snd_split[0] + " "
        keyword_list = [
            fst + snd_split[1],
            snd + snd_split[1]
        ]
    # TODO: Handle affixes with specific notation in future?
    else:
        keyword_list = [keywords]

    return keyword_list


def get_keyword_dict():
    """
    Reads the given keyword hierarchy into a dictionary for inference.

    The dictionary contains mappings of keyword categories to lists
    of keywords in order to automatically detect "parent" keywords.

    Returns:
        keyword_dict (dict[str, list[str]])
    """
    with open(file_path, "r") as f:
        category = None
        keyword_dict = {}
        lines = f.readlines()
        for line in lines:
            current_category = [
                cat for cat in keyword_categories if cat in line
            ]
            if current_category:
                category = current_category
                assert len(category) == 1
                category = category[0]
            else:
                indentation = 0
                for c in line:
                    indentation += 1 if c == " " or not c.isascii() else 0
                    if c.isalpha():
                        break
                # Highest indentation signifies keyword
                if (
                    indentation == 12
                    or category == "social sciences" and indentation == 8
                ):
                    keyword = "".join(c for c in line if ord(c) < 128)
                    keyword = keyword.split("(")[0].strip()
                    keyword_dict[keyword] = category

    return keyword_dict
