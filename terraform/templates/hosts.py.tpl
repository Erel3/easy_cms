
# all listed instances must be running on install and update
# run update if hosts configuration changed
# dns address can be used instead of ip

hosts = [
${ip_db},
${ip_lb},
${ip_ws},
${ip_wk},
]

# servers connection settings
user = "${ec2_username}"
key_filename = "~/Work/keys/${keyname}.pem"

localipmask = "${local_subnet}"

