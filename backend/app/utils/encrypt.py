#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

from typing import Any

from cryptography.hazmat.backends.openssl import backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from itsdangerous import URLSafeSerializer

from backend.app.common.log import log


class AESCipher:
    def __init__(self, key: bytes | str):
        """
        :param key: 키, 16/24/32 바이트 또는 16진수 문자열
        """
        self.key = key if isinstance(key, bytes) else bytes.fromhex(key)

    def encrypt(self, plaintext: bytes | str) -> bytes:
        """
        AES 암호화

        :param plaintext: 암호화되기 전 평문
        :return:
        """
        if not isinstance(plaintext, bytes):
            plaintext = str(plaintext).encode("utf-8")
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=backend)
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(cipher.algorithm.block_size).padder()  # type: ignore
        padded_plaintext = padder.update(plaintext) + padder.finalize()
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
        return iv + ciphertext

    def decrypt(self, ciphertext: bytes | str) -> str:
        """
        AES 복호화

        :param ciphertext: 복호화되기 전 암호문, 바이트 또는 16진수 문자열
        :return:
        """
        ciphertext = (
            ciphertext if isinstance(ciphertext, bytes) else bytes.fromhex(ciphertext)
        )
        iv = ciphertext[:16]
        ciphertext = ciphertext[16:]
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=backend)
        decryptor = cipher.decryptor()
        unpadder = padding.PKCS7(cipher.algorithm.block_size).unpadder()  # type: ignore
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        return plaintext.decode("utf-8")


class Md5Cipher:
    @staticmethod
    def encrypt(plaintext: bytes | str) -> str:
        """
        MD5 암호화

        :param plaintext: 암호화되기 전 평문
        :return:
        """
        import hashlib

        md5 = hashlib.md5()
        if not isinstance(plaintext, bytes):
            plaintext = str(plaintext).encode("utf-8")
        md5.update(plaintext)
        return md5.hexdigest()


class ItsDCipher:
    def __init__(self, key: bytes | str):
        """
        :param key: 키, 16/24/32 바이트 또는 16진수 문자열
        """
        self.key = key if isinstance(key, bytes) else bytes.fromhex(key)

    def encrypt(self, plaintext: Any) -> str:
        """
        ItsDangerous 암호화 (실패할 수 있으며, plaintext가 직렬화할 수 없는 경우 MD5로 암호화됨)

        :param plaintext: 암호화되기 전 평문
        :return:
        """
        serializer = URLSafeSerializer(self.key)
        try:
            ciphertext = serializer.dumps(plaintext)
        except Exception as e:
            log.error(f"ItsDangerous encrypt failed: {e}")
            ciphertext = Md5Cipher.encrypt(plaintext)
        return ciphertext

    def decrypt(self, ciphertext: str) -> Any:
        """
        ItsDangerous 복호화 (실패할 수 있으며, ciphertext를 역직렬화할 수 없는 경우 복호화 실패, 원래의 암호문 반환)

        :param ciphertext: 복호화되기 전 암호문
        :return:
        """
        serializer = URLSafeSerializer(self.key)
        try:
            plaintext = serializer.loads(ciphertext)
        except Exception as e:
            log.error(f"ItsDangerous decrypt failed: {e}")
            plaintext = ciphertext
        return plaintext
