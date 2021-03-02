"""az consumption summary"""

from datetime import datetime
import itertools
import json
from pathlib import Path
import sys
from typing import Dict, Any
import click

@click.group()
def entry_point():
    """`az consumption usage list` summarizer"""
    # pylint:disable=unnecessary-pass
    pass

@click.command()
@click.option(
        "--input-file",
        help="optional input json file")
@click.option(
        "--group-by",
        default="resource-group",
        help="group by 'resource-group' or 'type' (default 'resource-group')")
def costs(
        input_file: str = "",
        group_by: str = "resource-group") -> None:
    """Cost summary grouping from consumption"""

    consumption_data = _consumption_data_from_input(input_file=input_file)
    consumption_data = sorted(consumption_data, key=lambda x: x["instanceId"])

    instance_summary = []

    for key, group in itertools.groupby(consumption_data, key=lambda x: x["instanceId"]):
        cost = 0.0
        for group_item in group:
            cost += float(group_item["pretaxCost"])
        instance_summary.append(dict(
            instance_id=key,
            cost=cost,
            resource_group=_resource_group_from_instance_id(instance_id=key),
            resource_type=_resource_type_from_instance_id(instance_id=key)
        ))

    if group_by == "resource-group":
        group_by_func = lambda x: x["resource_group"]
    elif group_by == "type":
        group_by_func = lambda x: x["resource_type"]
    else:
        raise Exception("Unknown group by type")

    consumption_summary = []
    instance_summary = sorted(instance_summary, key=group_by_func)
    for key, group in itertools.groupby(instance_summary, key=group_by_func):
        cost = 0.0
        for group_item in group:
            cost += group_item["cost"]
        consumption_summary.append(dict(
            key=key,
            cost=cost
        ))

    consumption_summary = sorted(consumption_summary, key=lambda x: -x["cost"])

    for consumption_item in consumption_summary:
        print("{},{:,.2f}".format(consumption_item["key"], consumption_item["cost"]))

@click.command()
@click.option(
        "--input-file",
        help="optional input json file")
def timeline(input_file: str = "") -> None:
    """Billing period and timing summary"""

    consumption_data = _consumption_data_from_input(input_file=input_file)
    consumption_data = sorted(consumption_data, key=lambda x: x["billingPeriodId"])
    billing_periods = []
    for key, _ in itertools.groupby(consumption_data, key=lambda x: x["billingPeriodId"]):
        billing_periods.append(key.split("/")[-1])

    print(f"Billing period(s): {','.join(billing_periods)}")

    usage_start = None
    usage_end = None
    datetime_format = "%Y-%m-%dT%H:%M:%SZ"
    for data_item in consumption_data:
        usage_start_converted = datetime.strptime(data_item["usageStart"], datetime_format)
        usage_end_converted = datetime.strptime(data_item["usageEnd"], datetime_format)
        if not usage_start or usage_start_converted < usage_start:
            usage_start = usage_start_converted
        if not usage_end or usage_end_converted > usage_end:
            usage_end = usage_end_converted

    print(f"{usage_start} -> {usage_end}")

@click.command()
@click.option(
        "--input-file",
        help="optional input json file")
def total(input_file: str = "") -> None:
    """Get the total cost of all input data"""

    consumption_data = _consumption_data_from_input(input_file=input_file)
    cost = 0.0
    for data_item in consumption_data:
        cost += float(data_item["pretaxCost"])

    print("${:,.2f}".format(cost))

def _resource_group_from_instance_id(instance_id: str) -> str:
    """Parse the resource group from the instance ID"""

    instance_id_parts = instance_id.split("/")
    resource_group = "none"
    for idx, part in enumerate(instance_id_parts):
        if part == "resourceGroups":
            resource_group = instance_id_parts[idx + 1].lower()

    return resource_group

def _resource_type_from_instance_id(instance_id: str) -> str:
    """Parse the resource type from the instance ID"""

    return instance_id.split("/")[-2]

def _consumption_data_from_input(input_file: str) -> Dict[str, Any]:
    """Retrieve input data from either a file or stdin"""

    if not input_file and sys.stdin.isatty():
        print("You must either pass --input-file or stdin")
        sys.exit(1)

    if not sys.stdin.isatty():
        consumption_input = "".join(sys.stdin)
    else:
        with open(Path(input_file).resolve()) as input_file_handle:
            consumption_input = "".join(input_file_handle.readlines())

    return json.loads(consumption_input)

entry_point.add_command(costs)
entry_point.add_command(timeline)
entry_point.add_command(total)

if __name__ == "__main__":
    entry_point()
