"""Command-line interface.

Usage:
  python -m voicebot numbers                 # list your Vapi numbers + their IDs
  python -m voicebot list                    # list available patient scenarios
  python -m voicebot call --scenario refill  # run a single scenario
  python -m voicebot run                      # run ALL scenarios (the main command)
  python -m voicebot run --only refill,cancel # run just a subset
  python -m voicebot fetch --call-id <id>     # re-save artifacts for a past call
"""

from __future__ import annotations

import argparse
import sys

from . import config
from .scenarios import load_scenarios, get_scenario
from .runner import run_scenario, save_artifacts, wait_for_call
from .vapi_client import VapiClient


def cmd_numbers(_args) -> None:
    client = VapiClient()
    numbers = client.list_phone_numbers()
    if not numbers:
        print("No phone numbers found. Create a free number in the Vapi dashboard.")
        return
    print("Your Vapi phone numbers:")
    for n in numbers:
        print(f"  id={n.get('id')}   number={n.get('number')}   name={n.get('name', '')}")
    print("\nPut the id you want into VAPI_PHONE_NUMBER_ID in your .env.")


def cmd_list(_args) -> None:
    print("Available scenarios:")
    for s in load_scenarios():
        print(f"  {s['id']:<20} {s['name']}")


def cmd_call(args) -> None:
    client = VapiClient()
    scenario = get_scenario(args.scenario)
    run_scenario(client, scenario, index=args.index)


def cmd_run(args) -> None:
    client = VapiClient()
    scenarios = load_scenarios()
    if args.only:
        wanted = {s.strip() for s in args.only.split(",")}
        scenarios = [s for s in scenarios if s["id"] in wanted]
        if not scenarios:
            raise SystemExit("None of the requested scenario ids matched.")
    print(f"Running {len(scenarios)} scenario(s) against {config.TEST_NUMBER}\n")
    for i, scenario in enumerate(scenarios, start=args.index_start):
        try:
            run_scenario(client, scenario, index=i)
        except Exception as e:  # noqa: BLE001 - one bad call shouldn't kill the batch
            print(f"  ! scenario {scenario['id']} failed: {e}")
        print()
    print("All done. Recordings in ./recordings, transcripts in ./transcripts.")


def cmd_fetch(args) -> None:
    client = VapiClient()
    call = wait_for_call(client, args.call_id)
    scenario = get_scenario(args.scenario) if args.scenario else {"id": "adhoc", "name": ""}
    paths = save_artifacts(client, call, scenario, index=args.index)
    print(f"Saved: {paths}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="voicebot", description="Patient voice bot tester.")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("numbers", help="list your Vapi phone numbers and IDs")
    sub.add_parser("list", help="list available scenarios")

    c = sub.add_parser("call", help="run a single scenario")
    c.add_argument("--scenario", required=True, help="scenario id (see `list`)")
    c.add_argument("--index", type=int, default=1, help="number used in output filenames")

    r = sub.add_parser("run", help="run all scenarios")
    r.add_argument("--only", help="comma-separated scenario ids to run instead of all")
    r.add_argument("--index-start", type=int, default=1, help="starting file index")

    f = sub.add_parser("fetch", help="re-save artifacts for an existing call id")
    f.add_argument("--call-id", required=True)
    f.add_argument("--scenario", help="scenario id for labeling (optional)")
    f.add_argument("--index", type=int, default=1)

    return p


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv if argv is not None else sys.argv[1:])
    {
        "numbers": cmd_numbers,
        "list": cmd_list,
        "call": cmd_call,
        "run": cmd_run,
        "fetch": cmd_fetch,
    }[args.command](args)


if __name__ == "__main__":
    main()
