#!/usr/bin/env python3

import boto3
import json


# {
#     "Name": "analytics-upgrade.intouchstaging.com.",
#     "Type": "A",
#     "SetIdentifier": "analytics-upgrade.intouchstaging.com_IAD",
#     "MultiValueAnswer": true,
#     "TTL": 300,
#     "ResourceRecords": [
#         {
#             "Value": "170.176.144.153"
#         }
#     ],
#     "HealthCheckId": "579d73af-86d8-4276-827e-1219a4ea76a5"
# }


# apply changes or just test
# TRUE for testing
dry_run = True

# Return list of zones with filtered info, only ids and name
def get_list_of_zones(session):
    client = session.client('route53')

    # pag objects in case there's more than 100 zones
    paginator = client.get_paginator('list_hosted_zones')
    response_iterator = paginator.paginate(
                            PaginationConfig={
                                'MaxItems': 500,
                                'PageSize': 500
                            }
    )

    list_of_zones = []
    # iterates over each zone in each page
    # extracs id and adds only name and id to results
    for page in response_iterator:
        for each_zone in page['HostedZones']:
            zone_name = each_zone['Name']
            zone_id = each_zone['Id'].split('/')[-1]
            list_of_zones.append({'Name':zone_name, 'Id':zone_id})
    return(list_of_zones)

# Return a list of records
def get_list_of_records(zone_id, session):
    # set pag objects
    client = session.client('route53')
    paginator = client.get_paginator('list_resource_record_sets')
    response_iterator = paginator.paginate(HostedZoneId=zone_id)

    # iterates through pages and records
    list_of_records = []
    for page in response_iterator:
        for record in page['ResourceRecordSets']:
            list_of_records.append(record)
    return(list_of_records)

# Find all mv records for a given zone
def find_all_mv_records(zone_id, session):
    results = []
    target_types = {'A', 'AAAA'}
    list_of_records = get_list_of_records(zone_id, session)
    for each_record in list_of_records:
        if each_record['Type'] in target_types and 'MultiValueAnswer' in each_record \
                and each_record['MultiValueAnswer'] is True:
            results.append(each_record)
    return(results)

# main
def main():
    # creates aws api sessions params
    session = boto3.session.Session(profile_name='aws-prd')
    client = session.client('route53')

    # find all mv records for every zone
    list_of_zones = get_list_of_zones(session)
    all_mv_records = []
    for each_zone in list_of_zones:
        print(f"> Searching records in {each_zone['Name']}")
        all_mv_records = all_mv_records + find_all_mv_records(each_zone['Id'], session)

    # print out a list of all mv records in csv format
    #for every_record in all_mv_records:
    #    print(every_record['Name'] + ',' + every_record['ResourceRecords'][0]['Value'])

    print(json.dumps(all_mv_records[-6], indent=4))




if __name__ == '__main__':
    main()