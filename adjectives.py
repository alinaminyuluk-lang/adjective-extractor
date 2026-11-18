import re
import pymorphy3

morph = pymorphy3.MorphAnalyzer(lang="uk")

GENDER_MAP = {
    "masc": "чоловічий",
    "femn": "жіночий",
    "neut": "середній",
}

NUMBER_MAP = {
    "sing": "однина",
    "plur": "множина",
}

CASE_MAP = {
    "nomn": "називний",
    "gent": "родовий",
    "datv": "давальний",
    "accs": "знахідний",
    "ablt": "орудний",
    "loct": "місцевий",
    "voct": "кличний",
}


class TextValidationError(ValueError):
    pass


def validate_text(text: str) -> str:
    if text is None or not isinstance(text, str) or not text.strip():
        raise TextValidationError("Помилка: поле вводу порожнє. Введіть текст українською мовою.")

    cleaned = text.strip()
    if len(cleaned) < 3:
        raise TextValidationError("Помилка: текст занадто короткий (мінімум 3 символи).")

    if not re.search(r"[а-яіїєґА-ЯІЇЄҐ]", cleaned):
        raise TextValidationError(
            "Помилка: у тексті не знайдено слів українською мовою (лише цифри, символи або інша мова)."
        )

    return cleaned


def is_adjective(word: str) -> tuple[bool, dict]:
    parses = morph.parse(word)
    if not parses:
        return False, {}

    best = parses[0]
    if best.tag.POS in {"ADJF", "ADJS"}:
        gender = GENDER_MAP.get(best.tag.gender, "— (множина)")
        number = NUMBER_MAP.get(best.tag.number, "—")
        case = CASE_MAP.get(best.tag.case, "—")
        info = {
            "word": word,
            "lemma": best.normal_form,
            "gender": gender,
            "number": number,
            "case": case,
        }
        return True, info

    return False, {}


def extract_adjectives(text: str) -> dict:
    valid_text = validate_text(text)

    tokens = re.findall(r"[а-яіїєґА-ЯІЇЄҐ'’-]+|[^а-яіїєґА-ЯІЇЄҐ'’-]+", valid_text)

    highlighted_tokens = []
    adjectives_list = []
    total_words = 0

    for token in tokens:
        if re.fullmatch(r"[а-яіїєґА-ЯІЇЄҐ'’-]+", token):
            total_words += 1
            found, info = is_adjective(token)
            if found:
                highlighted_tokens.append((token, "Прикметник"))
                adjectives_list.append(info)
            else:
                highlighted_tokens.append((token, None))
        else:
            highlighted_tokens.append((token, None))

    adj_count = len(adjectives_list)
    percentage = round((adj_count / total_words) * 100, 2) if total_words > 0 else 0.0

    return {
        "highlighted": highlighted_tokens,
        "adjectives": adjectives_list,
        "total_words": total_words,
        "adj_count": adj_count,
        "percentage": percentage,
    }
