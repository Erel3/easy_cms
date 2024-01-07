## General
project_name = "easy_cms"

## VPC
aws_vpc_cidr_block = "10.69.0.0/16"

## EC2 Base
aws_ec2_user  = "ubuntu"

## EC2 DB Instances
aws_ec2_db_type  = "t2.2xlarge"

## EC2 LB Instances
aws_ec2_lb_type  = "t2.medium"

## EC2 WebServer Instances
aws_ec2_ws_type  = "t2.medium"
awc_ec2_ws_count = 4

## EC2 Worker Instances
aws_ec2_wk_type  = "t2.medium"
awc_ec2_wk_count = 13

## TAGs
default_tags = {
  Env     = "easy_cms"
  Product = "easy_cms"
}
inventory_file = "../config/hosts.py"
