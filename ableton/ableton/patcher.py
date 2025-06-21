
from dataclasses import dataclass
from pathlib import Path
from re import fullmatch as regex_fullmatch

@dataclass
class Patcher:
    """
    An executable patcher that replaces a factory signing key with an accessible signing key (so that it can be used with a keygen). 
    """
    application_path: str
    factory_key: int
    signing_key: int

    def __init__(self, *, application_path: str, factory: str, signing: str) -> None:
        self.application_path = Path(application_path)

        lhs, rhs = len(factory), len(signing)
        if lhs != rhs:
            raise ValueError(f'expected keys of identical length; received {lhs} != {rhs}')

        def __validate_form(k: str, type: str) -> None:
            if not regex_fullmatch(f'[0-9a-fA-f]+', k):
                raise ValueError(f'expected hexadecimal {type} key; received {k}')
            self.__setattr__(f"{type}_key", bytes.fromhex(k))

        __validate_form(factory, 'factory')
        __validate_form(signing, 'signing')

    def patch(self, revert: bool = False) -> None:
        """
        Opens the executable and replaces the factory key with the signing key via direct byte manipulation.
        """
        if revert:
            fk, sk = self.signing_key, self.factory_key
        else:
            fk, sk = self.factory_key, self.signing_key

        with open(self.application_path, 'rb') as ableton:
            content = ableton.read()
        
        if fk not in content:
            raise RuntimeError(f'expected factory key to appear in Ableton executable')
        
        content = content.replace(fk, sk)
        
        if fk in content:
            raise RuntimeError(f'the factory key is still present; is this executable protected or versioned?')
        
        with open(self.application_path, 'wb') as ableton:
            ableton.write(content)
