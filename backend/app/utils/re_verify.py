def search_string(pattern, text) -> bool:
    """
    전체 필드 정규식 일치

    :param pattern:
    :param text:
    :return:
    """
    result = re.search(pattern, text)
    if result:
        return True
    else:
        return False


def match_string(pattern, text) -> bool:
    """
    필드 시작 정규식 일치

    :param pattern:
    :param text:
    :return:
    """
    result = re.match(pattern, text)
    if result:
        return True
    else:
        return False


def is_phone(text: str) -> bool:
    """
    핸드폰 번호 확인

    :param text:
    :return:
    """
    return match_string(r"^1[3-9]\d{9}$", text)
