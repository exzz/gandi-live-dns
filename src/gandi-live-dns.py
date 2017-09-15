#!/usr/bin/env python2
# encoding: utf-8
'''
Gandi v5 LiveDNS - DynDNS Update via REST API and CURL/requests

@author: cave
@author: Nicolas Leclercq
License GPLv3
https://www.gnu.org/licenses/gpl-3.0.html

Created on 13 Aug 2017
http://doc.livedns.gandi.net/
'''
from __future__ import print_function
import requests, json
import config
import argparse
import dns.resolver


def get_pubip(type='ipv4'):

    rdtype = ('AAAA' if type == 'ipv6' else 'A')
    servers = (['2620:0:ccc::2', '2620:0:ccd::2'] if type == 'ipv6' else ['208.67.222.222', '208.67.220.220'])

    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = servers
    try:
        answers = resolver.query('myip.opendns.com', rdtype)
    except dns.exception.DNSException as e:
        print('Cannot get public', type, ':', e)
        exit(1)

    return answers[0].address

def get_uuid():
    '''
    find out ZONE UUID from domain
    Info on domain "DOMAIN"
    GET /domains/<DOMAIN>:

    '''
    url = config.api_endpoint + '/domains/' + config.domain
    try:
        headers = {"X-Api-Key":config.api_secret}
        u = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        print('Cannot get', config.domain, 'uuid', ':', e)

    json_object = json.loads(u._content)
    if u.status_code == 200:
        return json_object['zone_uuid']
    else:
        print('Cannot get', config.domain, 'uuid', ':', json_object['message'])
        exit(1)

def get_dnsip(uuid, type='ipv4'):
    ''' find out IP from first Subdomain DNS-Record
    List all records with name "NAME" and type "TYPE" in the zone UUID
    GET /zones/<UUID>/records/<NAME>/<TYPE>:

    The first subdomain from config.subdomain will be used to get
    the actual DNS Record IP
    '''

    rdtype = ('AAAA' if type == 'ipv6' else 'A')
    url = config.api_endpoint+ '/zones/' + uuid + '/records/' + config.subdomains[0] + '/' + rdtype
    try:
        headers = {"X-Api-Key":config.api_secret}
        u = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        print('Cannot get', type, 'from subdomain', config.subdomains[0], ':', e)
        exit(1)

    json_object = json.loads(u._content)
    if u.status_code == 200:
        return json_object['rrset_values'][0].encode('ascii','ignore').strip('\n')
    else:
        print('Cannot get', type, 'from subdomain', config.subdomains[0], ':', json_object['message'])
        exit(1)

def update_records(uuid, ip, subdomain, type='ipv4'):
    ''' update DNS Records for Subdomains
        Change the "NAME"/"TYPE" record from the zone UUID
        PUT /zones/<UUID>/records/<NAME>/<TYPE>:
        curl -X PUT -H "Content-Type: application/json" \
                    -H 'X-Api-Key: XXX' \
                    -d '{"rrset_ttl": 10800,
                         "rrset_values": ["<VALUE>"]' \
                    https://dns.beta.gandi.net/api/v5/zones/<UUID>/records/<NAME>/<TYPE>
    '''

    rdtype = ('AAAA' if type == 'ipv6' else 'A')
    url = config.api_endpoint+ '/zones/' + uuid + '/records/' + subdomain + '/' + rdtype
    payload = {"rrset_ttl": config.ttl, "rrset_values": [ip]}
    headers = {"Content-Type": "application/json", "X-Api-Key":config.api_secret}
    try:
        u = requests.put(url, data=json.dumps(payload), headers=headers)
    except requests.exceptions.RequestException as e:
        print('Cannot update', subdomain, ':', e)
        exit(1)

    json_object = json.loads(u._content)
    if u.status_code != 201:
        print('Cannot update', subdomain, ':', json_object['message'])
        exit(1)

def main(enable_ipv6, force_update):

    #get zone ID from Account
    uuid = get_uuid()

    todo_type= ['ipv4']
    if enable_ipv6:
        todo_type.append('ipv6')

    for type in todo_type:

        pubip = get_pubip(type)
        verboseprint('Public', type, 'is', pubip)

        dnsip = get_dnsip(uuid, type)
        verboseprint('DNS', type, 'is', dnsip)

        if force_update or (pubip != dnsip):
            for sub in config.subdomains:
                update_records(uuid, pubip, sub, type)
                print('DNS record', sub, 'updated to', pubip)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-6', '--ipv6', help="Enable ipv6 support", action="store_true")
    parser.add_argument('-v', '--verbose', help="increase output verbosity", action="store_true")
    parser.add_argument('-f', '--force', help="force an update/create", action="store_true")
    args = parser.parse_args()

    verboseprint = print if args.verbose else lambda *a, **k: None


    main(args.ipv6, args.force)






