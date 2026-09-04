"""Freeze Noema's source-backed Batch 02 case review and aggregate evidence."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


CONFIRMED = {
    "6567d9c242bb3ca00c9efb0b1ab57a2b08b7da4f92dc8fd1d73820e6aa0f5e72": "A whitelisted function opens its caller-supplied file_path directly for writing.",
    "03b2f51451967eaef1e9c936c2bb39d4646c68c5dcbe761d92fed1f0939ac304": "An f-string containing database_name is passed to the explicit shell helper.",
    "8cef2c6312d18f570cbf567518d6fbf82c6f518e1fdf7622f6f9726035b30c2f": "An f-string containing sql_file_path is passed to the explicit shell helper.",
    "baec525f28776b2b8aadb4c6b21655d6339e1a84b2dcd81389add8c776d466f2": "An f-string containing files_path is passed to the explicit shell helper.",
    "f465be6ebef94b08ac2c64026bdfcb7a788f1f160d679260cdc0eb2ad12058dd": "An f-string containing sql_file_path is passed to the explicit shell helper.",
}

INTENTIONAL = {
    "3b6460301ce607851db4e7ddc17ed72f2cdeeac3ff1311537a9685e8f7a8c932": "An administrator CLI command deliberately reads its resolved input path.",
    "030e27866169aca0dcfa7f73aae4e7eed580044f7b30ce194a87c34345a2fcea": "This generic framework helper deliberately reads the path supplied by its trusted caller.",
    "056094db4d375844a0b4125e288377763ccce75fabe9351eabbd6df9c419751a": "A migration patch deliberately reads paths produced by its own glob.",
    "1a6704a7acb1211c038596e6b8e2a177f1a5fc0e074e31d7a900357e4b166ff3": "The installer deliberately accepts an operator-provided restore file path.",
    "2eec2b1cc021e5d7ff97f7228fd6371613ad3ee388f7c807f49ba0d0d652c954": "This generic framework helper deliberately reads the path supplied by its trusted caller.",
    "08a1e0f969db73d85ca62c3be554d040baf5f98a95300044d460188d4c84600d": "The export routine deliberately writes to its internally selected export path.",
    "09b5105b628613b9b3306108859d725bb98040b7a14b3b1f42fb71a88c11e373": "The export routine deliberately writes to its internally selected export path.",
    "096d251dac9e16334c255f8ddb4a2df4e79f1fbb29c801b182bed40e5db58c7d": "The migration utility deliberately reads from its operator-selected migration root.",
    "c5502d9bcdd552ab786a6d25ee3314d8237af5d9681b7ecd9b8d9a6a04c0811a": "The migration utility deliberately reads files enumerated beneath its migration root.",
    "eea6a58063e09a3bcb363f94069900aace4bd04fdedbc1c8a928208e76a9a109": "The migration utility deliberately reads an asset path derived from migrated content.",
    "f3313341a0e54bf5eb15009b01e966ca5e3860dd60c26f8ac7d61c97670d4f78": "A generic administrator CLI helper deliberately exposes process execution to its caller.",
    "cea13af9a72c44251d4995f070d90cf3eaf67fee5acd5b77ab3da0af144544ef": "A repository-maintenance helper deliberately executes its shlex-split command; no production caller was found.",
    "e2aea279fcf30bec465ef7d51b39faa4253b666e33c10c91a3b7fc4e32c83fc1": "This is the framework's explicit shell-execution sink, not evidence about any individual caller.",
}

SAFE_BASES = {
    "170de9176cdb92e416a3fd5330c947c3c5b17d7a1309ef320a3c671c5c0557af": "The demo hook reads an internally constructed fixture path.",
    "a6b388cb6b33d4752df586c526d92ef2691eff067ed1bac0e1c2f46fcca1656f": "The importer reads its repository-owned sample CSV path.",
    "0215343164d452c6a9db3f06a482c8af8b397ea46ba76a6cee97e046776be9e8": "The patch reads a fixed file beneath its application path.",
    "2a155d8c0ba3226ac40686fff3c14d00d35f4c00e501487d305186e7f638d924": "Setup reads a fixed fixture beneath its application path.",
    "1c45eca604f65bb458dc59d2f07c384329e67bccd6ba785c0eb6f33ee2cba514": "File.get_full_path supplies a framework-resolved managed file path.",
    "1c75fe094e7bbbef83fc562ba2e91d884696eed827cbd054bd58ffd40681de19": "The path comes from an internal template-file enumeration.",
    "dcd33477cadf6a423bb5d18a2ccec6adedb9dd3223180c1f1dfe397e674309bd": "frappe.uploaded_file is the framework-managed temporary upload handle.",
    "82bd3564942b729888605569ceeabfc35af2a68ffc5beb0b2c1e5c126e0e250a": "The generator writes to its internally constructed repository destination.",
    "8129e428d51cc042d5343e33994580761258304c26eb95bde90e1114a8f821b9": "The temporary output name is generated from an internal hash.",
    "9a4227b97783bbad824643414ffe27bed60a992b91deb62e0d63c276d3c783ce": "The output path is selected by the internal report-template generator.",
    "46773ca55b19c0d6778c50640724d538f3574803cc4da3f45a28d2fad242b258": "The filename is selected from a fixed licence allowlist.",
    "07f5fb278949376e9de4987b08a565d2b62830c169664116d23eb5d6a11d562b": "Metadata is read from a path resolved beneath an installed application.",
    "410d5f8e81cbfaf8e82f9eec30c5e4cb339b5500745e350d13d63039d622823b": "Module metadata is read from a path resolved beneath its application.",
    "e2e6292e7a7a47fc60d442289722dd2da43e7badbe33687fb59b14058ade0cf7": "StaticPage resolves the path and proves it remains beneath the application root before reading.",
    "5bceab1448311e6697aea482baf9e9dc8d4691c1097be861905a1628950f815b": "The read targets the fixed procfs path for the current parent process.",
    "9c5979ee9307358413375a35292ca9074b3368c34b3e11806b9506b837bb3379": "The testing helper reads the fixed pyproject file beneath a selected application.",
    "284e4ba370f02819ce202d1f80f1647d5558b51748bfac4cd4fc11b69d37d8a8": "The fixed /dev/null target is not a traversal boundary.",
    "6464178b6aed22e96d187a2e4af3c46e858919f25deb77cda00a9ed4a5d1c34f": "The fixed /dev/null target is not a traversal boundary.",
    "09c14c389875206653ba11fd17722a93fe1777c2024c17795c2d97076a67772b": "Boilerplate writes to an internally constructed destination.",
    "0c01e591840e9f110ac3dc1ff4b5e1a88e508db0f8cf3993f0632dc36c9621b0": "Boilerplate writes to an internally constructed destination.",
    "8df83b71213abe4d85987dbc2fe1e069e7ed7ed01176b5fac795ce9da4ce72c6": "The package output is resolved beneath the framework-managed site path.",
    "dc1bffd93c781f7cdea49dc64afffbd8a37ab453e9714d6927f0db3284deeda5": "The package output is resolved beneath the framework-managed site path.",
    "38d0bd3d59afcd6dc4b063f6c37454b3255fb338190e29af9158e1b1028a0602": "The setup log uses a fixed filename.",
    "615f434d7ee58c3d8d916e3c8dd9dd63cb42e92f9c40f23b300240793d0ab1fb": "The identicon helper uses a fixed temporary filename.",
    "c795335d99c28ccc71f18837d2594be132a08658b325906638c613983f8f8bec": "The suppressed local_path is validated against the expected manifest-controlled cache location before use.",
    "4adaca8992cafa6ddb9c6c2525995a84b2828103aa16f8932d096715c69918fb": "Chrome receives a locally constructed argument vector without a shell.",
    "552bb1878ee683473a38d0953cef27635c890a02665f523ff86f16943f3d79a0": "Chrome receives a locally constructed Windows argument vector without a shell.",
    "3ece3efd54dae46bdef0bf0873aaea6b952b9fd26ea38c796e31ccb04b53abe0": "The command is a fixed pip-freeze argument list.",
    "464a3d57a779d63b39e8a441b4f243160712f392b135f500357f0f62ac65524f": "The move command uses a fixed executable and separate framework-managed path arguments.",
    "471003fa33da1178da151c3ed400c3195d2eb805a66cff71ffd53b02e9b96ffd": "The git command uses a fixed executable and separate application argument.",
    "557bd7879aaac8babdbdf7f8f0bf2817bbdcdaf17a381d84d08265565bdf868a": "The command is a fixed wkhtmltopdf version argument list.",
    "769e5c55c49f4ef206b7c71d554541b3cd471ce2e2a3c15fdeaa0113c7517c9f": "The command is a fixed pip-install argument list.",
    "897e683aa7330df29db7ce401f6fec140b38bf6b5653f33c25fe1c0fda88c466": "The command is a fixed wkhtmltopdf version argument list.",
    "ce01806fc7ccabf8dc74b3b94fa74254e2a4334ca4a01ff8c664c74418c0a1a3": "Tar receives a fixed operation and a separate framework-managed archive path.",
    "d110a2eee0293469c5d5613ca4d25a606624b3ab55293a45e5637cc16c6296c8": "Tar receives a fixed operation and separate internally controlled restore paths.",
    "d5cb79a7abd0dec45f367067e6aa7d47f9c042edf54c7ae7f22dc4f402520c6d": "The git command uses a fixed executable and separate application argument.",
    "ea59e71021e1debc4caf0884dc167de8f28f311de6307f20f8f724189ba2bd2a": "Tar receives a fixed operation and separate internally controlled restore paths.",
    "92d527b7b5e74c57a1c7c1fcd7d4cb7f7181369146833d62deefff2d9f5416a1": "Node receives a locally constructed argument vector; dynamic content is a separate argv value, not shell text.",
}


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    queue = json.loads(args.queue.read_text())
    expected = set(CONFIRMED) | set(INTENTIONAL) | set(SAFE_BASES)
    actual = {row["case_id"] for row in queue["records"]}
    if actual != expected:
        raise ValueError(f"case disposition mismatch: missing={sorted(actual - expected)}, stale={sorted(expected - actual)}")

    reviews = []
    for record in queue["records"]:
        case_id = record["case_id"]
        if case_id in CONFIRMED:
            label, basis = "confirmed-issue", CONFIRMED[case_id]
        elif case_id in INTENTIONAL:
            label, basis = "intentional-policy", INTENTIONAL[case_id]
        else:
            label, basis = "safe-near-miss", SAFE_BASES[case_id]
        reviews.append({"basis": basis, "case_id": case_id, "label": label})

    review = {
        "batch_id": queue["batch_id"],
        "cases": reviews,
        "review_author": "Noema",
        "review_scope": "structural source claims only; no exploitability assertion",
        "review_state": "authored-frozen",
        "schema_version": 1,
    }
    rule_evidence = []
    for rule_id in ("frappe-security-file-traversal", "frappe-subprocess-exec"):
        selected_ids = {row["case_id"] for row in queue["records"] if row["rule_id"] == rule_id}
        counts = Counter(row["label"] for row in reviews if row["case_id"] in selected_ids)
        if rule_id == "frappe-security-file-traversal":
            finding = "The upstream open-call inventory does not establish traversal. One independent search found a whitelisted direct path-to-write boundary that supports a separate narrow claim."
            population = queue["finding_populations"][rule_id]
        else:
            finding = "The backport process-call inventory mixes safe argument vectors, intentional execution wrappers and shell helpers. Four independent searches support a separate interpolated-shell-helper claim."
            population = queue["finding_populations"][rule_id]
        rule_evidence.append({
            "finding": finding,
            "labels": dict(sorted(counts.items())),
            "population": population,
            "rule_id": rule_id,
            "sample": len(selected_ids),
        })
    evidence = {
        "batch_id": queue["batch_id"],
        "limitations": [
            "The file-call population is deterministically sampled and cannot support blocking enforcement.",
            "Static source establishes structural boundaries, not runtime exploitability, reachability or business impact.",
            "The process-call population is complete for current findings, but independent search is bounded to direct Python call structures.",
        ],
        "review_author": "Noema",
        "review_queue": str(args.queue),
        "review_state": "authored-frozen",
        "rules": rule_evidence,
        "schema_version": 1,
    }
    write_json(args.review, review)
    write_json(args.evidence, evidence)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
