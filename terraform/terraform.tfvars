##General
project_name = "easy_cms"

##VPC Vars
aws_vpc_cidr_block = "10.69.0.0/16"

##EC2 Vars
aws_ec2_type = "t2.medium"
aws_ec2_user = "ubuntu"
awc_ec2_count = 2

##TAGs
default_tags = {
  Env     = "easy_cms"
  Product = "easy_cms"
}
inventory_file = "../config/hosts.py"
