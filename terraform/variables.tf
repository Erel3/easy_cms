variable "AWS_SSH_KEY_NAME" {
  description = "Name of the SSH keypair to use in AWS."
}

variable "AWS_DEFAULT_REGION" {
  description = "AWS Region"
}

/*
* General Settings
*
*/
variable "project_name" {
  description = "Project name. will be used in all resource names"
}

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

/*
* AWS VPC Variables
*
*/
variable "aws_vpc_cidr_block" {
  description = "CIDR Block for VPC"
}

/*
* EC2 Variables
*
*/
variable "aws_ec2_type" {
  description = "Instance type"
}

variable "aws_ec2_user" {
  description = "ec2-instance-user"
}
variable  "awc_ec2_count" {
  description = "Ec2 instance count"
  type = number
}

/*
* TAGs
*
*/
variable "default_tags" {
  description = "Default tags for all resources"
  type        = map
}

/*
* Inventory File
*
*/
variable "inventory_file" {
  description = "Where to store the generated inventory file"
}
