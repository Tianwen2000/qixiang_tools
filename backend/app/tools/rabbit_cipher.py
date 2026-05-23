from dataclasses import dataclass

from app.core.exceptions import AppException
from app.utils.crypto_utils import format_bytes, parse_bytes


TOOL_META = {
    "slug": "rabbit-cipher",
    "name": "Rabbit 加密/解密",
    "category": "encode",
    "input_mode": "text",
    "result_type": "text",
}


WORD_MASK = 0xFFFFFFFF
COUNTER_CONSTANTS = [
    0x4D34D34D,
    0xD34D34D3,
    0x34D34D34,
    0x4D34D34D,
    0xD34D34D3,
    0x34D34D34,
    0x4D34D34D,
    0xD34D34D3,
]


def _rotl32(value: int, shift: int) -> int:
    return ((value << shift) | (value >> (32 - shift))) & WORD_MASK


def _g_function(u: int, v: int) -> int:
    summed = (u + v) & WORD_MASK
    squared = (summed * summed) & 0xFFFFFFFFFFFFFFFF
    return ((squared >> 32) ^ (squared & WORD_MASK)) & WORD_MASK


def _concat16(high: int, low: int) -> int:
    return ((high & 0xFFFF) << 16) | (low & 0xFFFF)


@dataclass
class RabbitState:
    x: list[int]
    c: list[int]
    b: int

    def clone(self) -> "RabbitState":
        return RabbitState(self.x[:], self.c[:], self.b)


class RabbitCipher:
    def __init__(self, key: bytes, iv: bytes | None = None) -> None:
        if len(key) != 16:
            raise AppException(message="Rabbit 密钥长度必须正好是 16 字节", code=4001, status_code=400)
        if iv is not None and len(iv) != 8:
            raise AppException(message="Rabbit 的 IV 长度必须正好是 8 字节", code=4001, status_code=400)

        self.master = self._key_setup(key)
        self.state = self.master.clone()
        if iv is not None:
            self._iv_setup(iv)

    def _subkeys(self, key: bytes) -> list[int]:
        return [int.from_bytes(key[14 - 2 * index : 16 - 2 * index], "big") for index in range(8)]

    def _key_setup(self, key: bytes) -> RabbitState:
        subkeys = self._subkeys(key)
        x = [0] * 8
        c = [0] * 8
        for index in range(8):
            if index % 2 == 0:
                x[index] = _concat16(subkeys[(index + 1) % 8], subkeys[index])
                c[index] = _concat16(subkeys[(index + 4) % 8], subkeys[(index + 5) % 8])
            else:
                x[index] = _concat16(subkeys[(index + 5) % 8], subkeys[(index + 4) % 8])
                c[index] = _concat16(subkeys[index], subkeys[(index + 1) % 8])

        state = RabbitState(x=x, c=c, b=0)
        for _ in range(4):
            self._next_state(state)
        for index in range(8):
            state.c[index] ^= state.x[(index + 4) % 8]
        return state

    def _iv_setup(self, iv: bytes) -> None:
        upper = int.from_bytes(iv[:4], "big")
        lower = int.from_bytes(iv[4:], "big")
        iv_values = [
            lower,
            _concat16((upper >> 16) & 0xFFFF, (lower >> 16) & 0xFFFF),
            upper,
            _concat16(upper & 0xFFFF, lower & 0xFFFF),
        ]
        self.state = self.master.clone()
        for index in range(8):
            self.state.c[index] ^= iv_values[index % 4]
        for _ in range(4):
            self._next_state(self.state)

    def _counter_update(self, state: RabbitState) -> None:
        carry = state.b
        for index in range(8):
            temp = state.c[index] + COUNTER_CONSTANTS[index] + carry
            state.c[index] = temp & WORD_MASK
            carry = temp >> 32
        state.b = carry

    def _next_state(self, state: RabbitState) -> None:
        self._counter_update(state)
        g_values = [_g_function(state.x[index], state.c[index]) for index in range(8)]
        state.x = [
            (g_values[0] + _rotl32(g_values[7], 16) + _rotl32(g_values[6], 16)) & WORD_MASK,
            (g_values[1] + _rotl32(g_values[0], 8) + g_values[7]) & WORD_MASK,
            (g_values[2] + _rotl32(g_values[1], 16) + _rotl32(g_values[0], 16)) & WORD_MASK,
            (g_values[3] + _rotl32(g_values[2], 8) + g_values[1]) & WORD_MASK,
            (g_values[4] + _rotl32(g_values[3], 16) + _rotl32(g_values[2], 16)) & WORD_MASK,
            (g_values[5] + _rotl32(g_values[4], 8) + g_values[3]) & WORD_MASK,
            (g_values[6] + _rotl32(g_values[5], 16) + _rotl32(g_values[4], 16)) & WORD_MASK,
            (g_values[7] + _rotl32(g_values[6], 8) + g_values[5]) & WORD_MASK,
        ]

    def _keystream_block(self) -> bytes:
        self._next_state(self.state)
        x = self.state.x
        words = [
            (x[0] ^ (x[5] >> 16) ^ ((x[3] << 16) & WORD_MASK)) & WORD_MASK,
            (x[2] ^ (x[7] >> 16) ^ ((x[5] << 16) & WORD_MASK)) & WORD_MASK,
            (x[4] ^ (x[1] >> 16) ^ ((x[7] << 16) & WORD_MASK)) & WORD_MASK,
            (x[6] ^ (x[3] >> 16) ^ ((x[1] << 16) & WORD_MASK)) & WORD_MASK,
        ]
        return b"".join(word.to_bytes(4, "big") for word in reversed(words))

    def crypt(self, data: bytes) -> bytes:
        output = bytearray()
        offset = 0
        while offset < len(data):
            block = self._keystream_block()
            chunk = data[offset : offset + 16]
            output.extend(byte ^ stream for byte, stream in zip(chunk, block))
            offset += len(chunk)
        return bytes(output)


def _split_iv_and_cipher(text: str, output_encoding: str) -> tuple[bytes | None, bytes]:
    parts = [item.strip() for item in text.strip().split(":") if item.strip()]
    if len(parts) == 2:
        iv = parse_bytes(parts[0], output_encoding, "iv")
        cipher_bytes = parse_bytes(parts[1], output_encoding, "cipher")
        return iv, cipher_bytes

    return None, parse_bytes(text, output_encoding, "cipher")


def run(
    text: str,
    action: str = "encrypt",
    key_text: str = "",
    key_encoding: str = "utf8",
    iv_text: str = "",
    iv_encoding: str = "utf8",
    output_encoding: str = "base64",
    **_: dict,
) -> str:
    key = parse_bytes(key_text, key_encoding, "key")

    if action == "encrypt":
        iv = parse_bytes(iv_text, iv_encoding, "iv") if iv_text.strip() else None
        cipher = RabbitCipher(key=key, iv=iv)
        encrypted = cipher.crypt(text.encode("utf-8"))
        encoded_cipher = format_bytes(encrypted, output_encoding, "cipher")
        if iv is None:
            return encoded_cipher
        return f"{format_bytes(iv, output_encoding, 'iv')}:{encoded_cipher}"

    if action == "decrypt":
        iv, cipher_bytes = _split_iv_and_cipher(text, output_encoding)
        if iv is None and iv_text.strip():
            iv = parse_bytes(iv_text, iv_encoding, "iv")
        cipher = RabbitCipher(key=key, iv=iv)
        try:
            return cipher.crypt(cipher_bytes).decode("utf-8")
        except Exception as exc:
            raise AppException(message=f"Rabbit 解密失败：{exc}", code=4001, status_code=400) from exc

    raise AppException(message="操作方式无效", code=4001, status_code=400)
