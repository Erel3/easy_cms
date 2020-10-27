
# all listed instances must be running on install and update
# run update if hosts configuration changed
# dns address can be used instead of ip

hosts = [
{"ip": "12.34.56.78", "workers": 0, },
{"ip": "23.45.67.89", "workers": 1, },
]

# servers connection settings
user = "ubuntu"
key_filename = "~/work/keys/server.pem"

localipmask = "172.31.0.0/16"


