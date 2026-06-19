import hashlib


def pmn_extra(
    *,
    func: str,
    trigger_method: str,
    brief_des: str,
    detail_des: str,
) -> dict[str, dict[str, str]]:
    return {
        "pmn": {
            "func": func,
            "trigger_method": trigger_method,
            "trigger_condition": "指令",
            "brief_des": brief_des,
            "detail_des": detail_des,
        },
    }


def check_md5(data: bytes, hash_value: str) -> bool:
    return not hash_value or hashlib.md5(data).hexdigest() == hash_value  # noqa: S324
