
# all listed instances must be running on install and update
# run update if hosts configuration changed
# dns address can be used instead of ip

hosts = [
${ip_alpha},
${ip_beta},
]

# servers connection settings
user = "${ec2_username}"
key_filename = "~/work/keys/${keyname}.pem"

localipmask = "${local_subnet}"

