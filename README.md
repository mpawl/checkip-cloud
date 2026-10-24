# checkip.cloud

checkip.cloud is a simple web interface and API implementation of for [`cloud_ip_checker.py`](https://github.com/mpawl/cloud-ip-checker). It is implemented in Docker. This is the system behind the publicly available service [checkip.cloud](https://checkip.cloud). This repository is associated with the following repository:
* [`cloud_ip_checker.py`](https://github.com/mpawl/cloud-ip-checker) is the logic behind this web implementation. 

## Data Sources

checkip.cloud queries against the following providers:

* Amazon Web Services (AWS)
* Google Services
* Google Cloud Platform (GCP)
* Microsoft Azure 
* Microsoft 365 (M365)
* Oracle Cloud Infrastructure (OCI)
* Digital Ocean
* Linode
* Cloudflare
* Fastly

See [`cloud_ip_checker.py`](https://github.com/mpawl/cloud-ip-checker) for more information on where this data comes from and how the data sources can be updated. 

The bundled provider data lives in [`cloud_ip_checker/cloud_ip_data/`](cloud_ip_checker/cloud_ip_data/). The checker resolves it relative to its Python module, so running from a different working directory does not change which data it uses. Set `CLOUD_IP_DATA_DIR` to use another data directory.

## Web UI

The web UI is simple. It takes an IP as input and prints output in a simple HTML table. 

## API

The API endpoint is available at `/api/ip/<ip here>`. A `JSON` object is returned to the query. Errors are returned if the IP is not found or if the input is not an IP address. 

Below is an example of the `JSON` output of a query using `curl`. 

```
curl -s http://<host>/api/ip/2620:1ec:4::152 | jq
{
  "ip": "2620:1ec:4::152",
  "matches": [
    {
      "provider": "Azure",
      "cidr": "2620:1ec:4::/46",
      "service": "AzureFrontDoor.FirstParty",
      "changeNumber": 20,
      "region": "",
      "regionId": 0,
      "platform": "Azure",
      "systemService": "AzureFrontDoor",
      "networkFeatures": [
        "API",
        "NSG",
        "UDR",
        "FW"
      ]
    },
    {
      "provider": "M365",
      "cidr": "2620:1ec:4::152/128",
      "serviceArea": "Exchange",
      "serviceAreaDisplayName": "Exchange Online",
      "id": 1,
      "urls": [
        "outlook.cloud.microsoft",
        "outlook.office.com",
        "outlook.office365.com"
      ],
      "tcpPorts": "80,443",
      "udpPorts": "443",
      "expressRoute": true,
      "category": "Optimize"
    },
    {
      "provider": "M365",
      "cidr": "2620:1ec:4::152/128",
      "serviceArea": "Exchange",
      "serviceAreaDisplayName": "Exchange Online",
      "id": 2,
      "urls": [
        "outlook.office365.com",
        "smtp.office365.com"
      ],
      "tcpPorts": "143, 587, 993, 995",
      "expressRoute": true,
      "category": "Allow",
      "notes": "POP3, IMAP4, SMTP Client traffic"
    }
  ]
}
```

## Development

Runtime and development dependencies are pinned in the generated requirements files. To install the test dependencies and run the regression suite:

```
python -m pip install --require-hashes -r requirements-dev.txt
python -m pytest
```

The pinned source inputs are `requirements.in` and `requirements-dev.in`. After changing them, install `pip-tools` and regenerate the lock files with `pip-compile --generate-hashes --output-file=requirements.txt requirements.in` and `pip-compile --generate-hashes --output-file=requirements-dev.txt requirements-dev.in`.

<!-- managed cloud IP source URLs: start -->
## Manually maintained Microsoft data URLs

* Azure: https://download.microsoft.com/download/7/1/d/71d86715-5596-4529-9b13-da13a5de5b63/ServiceTags_Public_20261019.json
* Microsoft 365: https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7
<!-- managed cloud IP source URLs: end -->
