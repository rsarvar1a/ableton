
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import dsa, utils
from cryptography.hazmat.primitives.hashes import SHA1
from dataclasses import dataclass
from random import randint
from typing import List, Iterator

@dataclass
class DSAParams:
    """
    A specification for a DSA private key.
    """
    g: int
    p: int
    q: int
    x: int
    y: int

    def __init__(self, *, g: str, p: str, q: str, x: str, y: str) -> None:
        def __read_hex_param(param: str) -> int:
            return int(param, 16)
        self.g, self.p, self.q, self.x, self.y = tuple(map(__read_hex_param, [g, p, q, x, y]))

    def construct(self) -> dsa.DSAPrivateKey:
        """
        Returns the private key corresponding to this specification.
        """
        params = dsa.DSAParameterNumbers(self.p, self.q, self.g)
        pub = dsa.DSAPublicNumbers(self.y, params)
        pvt = dsa.DSAPrivateNumbers(self.x, pub)
        return pvt.private_key(backend=default_backend())

@dataclass
class AuzGenerator:
    """
    A tool that generates a .auz file for the given private key and program configuration.
    """
    version: int
    edition: int
    hardware_id: str
    
    Editions = {
        "Lite": 4,
        "Intro": 3,
        "Standard": 0,
        "Suite": 2
    }

    def __init__(self, *, version: int, edition: str, hardware_id: str) -> None:
        self.version = version
        self.edition = AuzGenerator.Editions[edition]
        self.hardware_id = hardware_id.upper()
        if len(self.hardware_id) == 24:
            self.hardware_id = "-".join(self.hardware_id[i:i+4] for i in range(0, 24, 4))
    
    def generate(self, *, key: dsa.DSAPrivateKey) -> Iterator[str]:
        """
        Creates the body of an Authorize.auz file for the given key.
        """
        def __generate_one(eid: int, vid: int) -> str:
            authorize = "{},{:02X},{:02X},Standard,{}"
            serial_no = self.__random_serial_num()
            message = authorize.format(serial_no, eid, vid, self.hardware_id)
            signature = self.__sign(key, message)
            return authorize.format(serial_no, eid, vid, signature)
        
        yield __generate_one(self.edition, self.version << 4)
        for new_eid in list(range(0x40, 0xff + 1)) + list(range(0x8000, 0x80ff + 1)):
            yield __generate_one(new_eid, 0x10)

    def __random_serial_num(self) -> str:
        """
        Generates a random Ableton serial number of the form 3aaA-bbbB-cccC-dddD-eeeE-ZZZZ, where:
            - aa, bbb, ccc, ddd, eee are random
            - A, B, C, D, E are group-local checksums
            - ZZZZ is the serial's global checksum
        """
        groups = [randint(0x3000, 0x3fff)] + list(map(lambda _i: randint(0x0000, 0xffff), range(4)))
        for i in range(5):
            groups[i] = self.__local_checksum(i, groups[i])
        z = self.__overall_checksum(groups)
        return "{:04X}-{:04X}-{:04X}-{:04X}-{:04X}-{:04X}".format(*groups, z)
    
    def __local_checksum(self, i: int, group: int) -> int:
        """
        Computes the local checksum and returns the adjusted group.
        """
        checksum = group >>  4 & 0xf ^ \
                   group >>  5 & 0x8 ^ \
                   group >>  9 & 0x7 ^ \
                   group >> 11 & 0xe ^ \
                   group >> 15 & 0x1 ^ \
                   i
        return group & 0xfff0 | checksum

    def __overall_checksum(self, groups: List[int]) -> int:
        """
        Computes the global checksum over all groups in the serial.
        """
        r = 0
        for i in range(20):
            gid, digit = divmod(i, 4)
            value = groups[gid] >> (digit * 8) & 0xff
            r ^= value << 8
            for _ in range(8):
                r <<= 1
                if r & 0x10000: r ^= 0x8005
        return r & 0xffff

    def __sign(self, key: dsa.DSAPrivateKey, message: str) -> str:
        """
        Signs a message using the given private key.
        """
        signature = key.sign(message.encode(), SHA1())
        r, s = utils.decode_dss_signature(signature)
        return f'{r:040X}{s:040X}'
