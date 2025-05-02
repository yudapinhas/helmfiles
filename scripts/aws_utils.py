from scripts.utils import run_command


def run_aws_command(cmd):
    cmd = "aws {cmd} --output json".format(cmd=cmd)
    return run_command(cmd, load_json=True)


def get_hosted_zones():
    res = run_aws_command("route53 list-hosted-zones")
    return res["HostedZones"]


def get_records_for_hosted_zone(zone_id):
    res = run_aws_command("route53  list-resource-record-sets --hosted-zone-id {zone_id}".format(zone_id=zone_id))
    return res["ResourceRecordSets"]
