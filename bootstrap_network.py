import os
from os import getenv
from typing import Iterable, NamedTuple, Optional, Sequence

from indy_common.config_helper import NodeConfigHelper
from indy_common.config_util import getConfig
from plenum.common.keygen_utils import initNodeKeysForBothStacks
from plenum.common.util import hexToFriendly
from plenum.common.signer_did import DidSigner


NODE_IP = getenv("NODE_IP", "127.0.0.1")
CLIENT_IP = getenv("CLIENT_IP", "127.0.0.1")


class NodeKeys(NamedTuple):
    pubkey: str
    verkey: str
    bls: str
    pop: str

    @property
    def pubkey_b58(self):
        return hexToFriendly(self.pubkey)

    @property
    def verkey_b58(self):
        return hexToFriendly(self.verkey)


TRUSTEE_HEADERS = ['Trustee name', 'Trustee DID', 'Trustee verkey']

class Trustee(NamedTuple):
    name: str
    did: str
    verkey: str


STEWARD_NODE_HEADERS = [
    "Steward DID",
    "Steward verkey",
    "Validator alias",
    "Node IP address",
    "Node port",
    "Client IP address",
    "Client port",
    "Validator verkey",
    "Validator BLS key",
    "Validator BLS POP",
]


class StewardNode(NamedTuple):
    did: str
    verkey: str
    alias: str
    node_ip: str
    node_port: int
    client_ip: str
    client_port: int
    validator_verkey: str
    validator_bls: str
    validator_bls_pop: str


def generate_steward_nodes() -> Sequence[StewardNode]:
    entries = []
    for i in range(1, 5):
        seed = f"000000000000000000000000Steward{i}".encode("ascii")
        did = DidSigner(seed=seed)
        keys = init_key(f"Node{i}", seed)
        entries.append(
            StewardNode(
                did=did.identifier,
                verkey=did.full_verkey,
                alias=f"Node{i}",
                node_ip=NODE_IP,
                node_port=9700 + (i * 2) - 1,
                client_ip=CLIENT_IP,
                client_port=9700 + (i * 2),
                validator_verkey=keys.verkey_b58,
                validator_bls=keys.bls,
                validator_bls_pop=keys.pop
            )
        )
    return entries


def generate_trustees() -> Sequence[Trustee]:
    entries = []
    for i in range(1, 5):
        seed = f"000000000000000000000000Trustee{i}".encode("ascii")
        did = DidSigner(seed=seed)
        entries.append(
            Trustee(
                name=f"Trustee{i}",
                did=did.identifier,
                verkey=did.full_verkey,
            )
        )
    return entries



def init_key(name: str, seed: Optional[bytes] = None, force: bool = False):
    config = getConfig()
    config_helper = NodeConfigHelper(name, config)

    os.makedirs(config_helper.keys_dir, exist_ok=True)

    try:
        keys = initNodeKeysForBothStacks(
            name, config_helper.keys_dir, seed, override=force
        )
        return NodeKeys(*keys)
    except Exception as ex:
        print(ex)
        exit()


def csv(headers: Sequence[str], entries: Sequence[Iterable]):
    headers_str = ",".join(headers)
    entries_strs = [
        ",".join(str(item) for item in entry) for entry in entries
    ]
    return "\n".join([headers_str, *entries_strs])


if __name__ == "__main__":
    trustee_csv = csv(TRUSTEE_HEADERS, generate_trustees())
    steward_node_csv = csv(STEWARD_NODE_HEADERS, generate_steward_nodes())
    with open("trustee.csv", "w") as trustee_file:
        trustee_file.write(trustee_csv)
    with open("steward.csv", "w") as steward_file:
        steward_file.write(steward_node_csv)
