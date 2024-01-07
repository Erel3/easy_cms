variable "AWS_SSH_KEY_NAME" { description = "Name of the SSH keypair to use in AWS." }
variable "AWS_DEFAULT_REGION" { description = "AWS Region" }

## General
variable "project_name" { description = "Project name. will be used in all resource names" }

data "aws_ami" "distro" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}

data "aws_availability_zones" "available" {}

## VPC
variable "aws_vpc_cidr_block" { description = "CIDR Block for VPC" }

## EC2 Base
variable "aws_ec2_user" { description = "Instance user" }

## EC2 Database Variables
variable "aws_ec2_db_type" { description = "Instance type" }

## EC2 LoadBalancer Variables
variable "aws_ec2_lb_type" { description = "Instance type" }

## EC2 WebServer Variables
variable "aws_ec2_ws_type" { description = "Instance type" }

variable "awc_ec2_ws_count" {
  description = "Instance count"
  type        = number
}

## EC2 Worker Variables
variable "aws_ec2_wk_type" { description = "Instance type" }

variable "awc_ec2_wk_count" {
  description = "Instance count"
  type        = number
}


## TAGs
variable "default_tags" {
  description = "Default tags for all resources"
  type        = map(any)
}

## Inventory File
variable "inventory_file" {
  description = "Where to store the generated inventory file"
}
