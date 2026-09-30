"""Create / promote / rollback the day13-chat prompt in the personal Langfuse project."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(REPO_ROOT / ".env")

from langfuse import Langfuse  # noqa: E402

NAME = "day13-chat"
V1 = "Feature={{feature}}\nDocs={{docs}}\nQuestion={{message}}"
V2 = (
    "Feature={{feature}}\nDocs={{docs}}\nQuestion={{message}}\n"
    "Answer in at most two concise sentences and cite the retrieved docs."
)


def show(client: Langfuse) -> None:
    for v in (1, 2):
        p = client.get_prompt(NAME, version=v, type="text", cache_ttl_seconds=0)
        print(f"version={p.version} labels={sorted(p.labels)}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["project", "create", "show", "promote", "rollback"])
    args = ap.parse_args()
    client = Langfuse()
    if args.action == "project":
        print("project:", client.api.projects.get().data[0].name)
    elif args.action == "create":
        client.create_prompt(name=NAME, prompt=V1, labels=["baseline", "production"], type="text",
                             commit_message="v1 baseline")
        client.create_prompt(name=NAME, prompt=V2, labels=["candidate"], type="text",
                             commit_message="v2 candidate: concise answer")
        show(client)
    elif args.action == "show":
        show(client)
    elif args.action == "promote":
        client.update_prompt(name=NAME, version=2, new_labels=["production"])
        show(client)
    elif args.action == "rollback":
        client.update_prompt(name=NAME, version=1, new_labels=["production"])
        show(client)
    client.flush()


if __name__ == "__main__":
    main()
