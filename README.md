gandi-live-dns
----

This is a simple dynamic DNS updater for the
[Gandi](https://www.gandi.net) registrar. It uses their [LiveDNS REST API](http://doc.livedns.gandi.net/) to update the zone file for a subdomain of a domain to point at the external IPv4 and IPv6 addresses of the computer it has been run from.

It found out public IPs using openDNS myip record

It requieres Python 2

With the new v5 Website, Gandi has also launched a new REST API which makes it easier to communicate via bash/curl or python/requests.  

### Configure

#### API Key
First, you must apply for an API key with Gandi. Visit 
https://account.gandi.net/en/ and apply for (at least) the production API 
key by following their directions.

#### A DNS Record 
Create the DNS A and AAAA Records in the GANDI Webinterface which you want to update if your IP changes.


#### Script Configuration
Then you'd need to configure the script in the src directory.
Copy `example.config.py` to `config.py`, and put it in the same directory as the script.

Edit the config file to fit your needs. 

##### api_secret
Start by retrieving your API Key from the "Security" section in new [Gandi Account admin panel](https://account.gandi.net/) to be able to make authenticated requests to the API.
api_secret = '---my_secret_API_KEY----'

##### domain
Your domain for the subdomains to be updated 


##### subdomains
All subdomains which should be updated. They get created if they do not yet exist.

``` 
subdomains = ["subdomain1", "subdomain2", "subdomain3"]
```
The first subdomain is used to find out the actual IP in the Zone Records. 

### Run the script
```
./gandi-live-dns.py -6 -v
Public ipv4 is 90.x.x.220
DNS ipv4 is 90.x.x.220
Public ipv6 is 2a01:cb19:x:x:216:6fff:fee4:8649
DNS ipv6 is 2a01:cb19:x:x:96de:80ff:fed7:6108
DNS record foo updated to 2a01:cb19:x:x:216:6fff:fee4:8649
```

### Build archlinux package
```
cd package
makepkg .
```

#### rune with systemd
```
systemd start gandi-live-dns.service
```

#### Enable systemd timer
```
systemd enable gandi-live-dns.timer
```

