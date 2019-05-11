
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

# polygon login to download tasks
pollogin = "mmirzayanov"
polpassword = "passw0rd"

# telegram bot
token = "?????????:???????????????????????????????????"
secret = "secret"

# other
localipmask = "172.31.0.0/16"
getlocalip_command = "ifconfig eth0 | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\\2/p'"
