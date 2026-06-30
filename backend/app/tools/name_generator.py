"""文件说明：实现「姓名生成器」工具的后端逻辑。"""

import random

from app.core.exceptions import AppException


TOOL_META = {
    "slug": "name-generator",
    "name": "姓名生成器",
    "category": "text",
    "input_mode": "text",
    "result_type": "text",
}


SURNAMES = list("赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳鲍史唐费廉岑薛雷贺倪汤滕殷罗毕郝安常乐于时傅皮卞齐康伍余元顾孟平黄和穆萧尹")
DOUBLE_SURNAMES = ["欧阳", "上官", "司马", "诸葛", "东方", "夏侯", "南宫", "慕容"]
MALE_GIVEN = [
    "子轩",
    "宇辰",
    "浩然",
    "景川",
    "泽宇",
    "嘉佑",
    "承安",
    "奕晨",
    "俊驰",
    "明远",
    "锦程",
    "思源",
]
FEMALE_GIVEN = [
    "雨桐",
    "若溪",
    "诗涵",
    "佳宁",
    "依诺",
    "语彤",
    "沐瑶",
    "可欣",
    "知夏",
    "安琪",
    "芷若",
    "梦洁",
]
NEUTRAL_GIVEN = [
    "安然",
    "知远",
    "书言",
    "清和",
    "念初",
    "星禾",
    "一诺",
    "星野",
]


def _random_surname(rng: random.Random) -> str:
    if rng.random() < 0.12:
        return rng.choice(DOUBLE_SURNAMES)
    return rng.choice(SURNAMES)


def _build_name(rng: random.Random, gender: str) -> str:
    if gender == "male":
        pool = MALE_GIVEN
    elif gender == "female":
        pool = FEMALE_GIVEN
    elif gender == "mixed":
        pool = MALE_GIVEN + FEMALE_GIVEN + NEUTRAL_GIVEN
    else:
        raise AppException(message="性别选项不支持", code=4001, status_code=400)
    return f"{_random_surname(rng)}{rng.choice(pool)}"


def run(text: str = "", count: int = 10, gender: str = "mixed", **_: dict) -> str:
    if count not in {1, 5, 10, 20}:
        raise AppException(message="生成数量只能是 1、5、10 或 20", code=4001, status_code=400)
    rng = random.SystemRandom()
    return "\n".join(_build_name(rng, gender) for _ in range(count))
