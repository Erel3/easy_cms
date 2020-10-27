terraform {
  required_version = ">= 0.13.0"
}

provider "aws" {
  region = var.AWS_DEFAULT_REGION
}

/*
* Virtual private cloud
*
*/
resource "aws_vpc" "vpc" {
  cidr_block = var.aws_vpc_cidr_block

  tags = merge(var.default_tags, map(
    "Name", "${var.project_name}-vpc"
  ))
}

resource "aws_subnet" "vpc-public-subnet" {
  vpc_id            = aws_vpc.vpc.id
  availability_zone = data.aws_availability_zones.available.names[0]
  cidr_block        = var.aws_vpc_cidr_block

  tags = merge(var.default_tags, map(
    "Name", "${var.project_name}-public"
  ))
}

resource "aws_internet_gateway" "vpc-internetgw" {
  vpc_id = aws_vpc.vpc.id

  tags = merge(var.default_tags, map(
    "Name", "${var.project_name}-internetgw"
  ))
}

resource "aws_route_table" "routetable-public" {
  vpc_id = aws_vpc.vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.vpc-internetgw.id
  }

  tags = merge(var.default_tags, map(
    "Name", "${var.project_name}-routetable-public"
  ))
}

resource "aws_route_table_association" "routetable-public" {
  subnet_id      = aws_subnet.vpc-public-subnet.id
  route_table_id = aws_route_table.routetable-public.id
}

/*
* Security Groups
*
*/
resource "aws_security_group" "cms-cg" {
  name   = "${var.project_name}-securitygroup"
  vpc_id = aws_vpc.vpc.id

  tags = merge(var.default_tags, map(
    "Name", "${var.project_name}-securitygroup"
  ))
}
resource "aws_security_group_rule" "allow-all-egress" {
  type              = "egress"
  from_port         = 0
  to_port           = 65535
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.cms-cg.id
}
resource "aws_security_group_rule" "allow-ssh-connections" {
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "TCP"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.cms-cg.id
}
resource "aws_security_group_rule" "allow-http" {
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "TCP"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.cms-cg.id
}
resource "aws_security_group_rule" "allow-https" {
  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "TCP"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.cms-cg.id
}
resource "aws_security_group_rule" "allow-all-local-ingress" {
  type              = "ingress"
  from_port         = 0
  to_port           = 65535
  protocol          = "TCP"
  cidr_blocks       = [var.aws_vpc_cidr_block]
  security_group_id = aws_security_group.cms-cg.id
}


/*
* Create EC2 Instance
*
*/
resource "aws_instance" "cms-alpha" {
  ami               = data.aws_ami.distro.id
  instance_type     = var.aws_ec2_type
  availability_zone = data.aws_availability_zones.available.names[0]
  subnet_id         = aws_subnet.vpc-public-subnet.id

  vpc_security_group_ids = [aws_security_group.cms-cg.id]

  key_name = var.AWS_SSH_KEY_NAME

  tags = merge(var.default_tags, map(
    "Name", "${var.project_name}-alpha",
    "Cluster", "${var.project_name}",
    "Role", "alpha"
  ))
}

resource "aws_instance" "cms-beta" {
  ami               = data.aws_ami.distro.id
  instance_type     = var.aws_ec2_type
  count             = var.awc_ec2_count
  availability_zone = data.aws_availability_zones.available.names[0]
  subnet_id         = aws_subnet.vpc-public-subnet.id
  associate_public_ip_address = true

  vpc_security_group_ids = [aws_security_group.cms-cg.id]

  key_name = var.AWS_SSH_KEY_NAME

  tags = merge(var.default_tags, map(
    "Name", "${var.project_name}-beta-${count.index}",
    "Cluster", "${var.project_name}",
    "Role", "beta-${count.index}"
  ))
}

resource "aws_eip" "cms-eip" {
  instance = aws_instance.cms-alpha.id
  vpc      = true
}

/*
* Create Hosts File For Ansible
*
*/
data "template_file" "inventory" {
  template = file("${path.module}/templates/hosts.py.tpl")

  vars = {
    ip_alpha = format("{\"ip\": \"%s\", \"workers\": 0, }", aws_eip.cms-eip.public_ip)
    ip_beta  = join(",\n", formatlist("{\"ip\": \"%s\", \"workers\": 1, }", aws_instance.cms-beta.*.public_ip))
    ec2_username = var.aws_ec2_user
    keyname = var.AWS_SSH_KEY_NAME
    local_subnet = var.aws_vpc_cidr_block
  }
}
resource "null_resource" "inventories" {
  provisioner "local-exec" {
    command = "echo '${data.template_file.inventory.rendered}' > ${var.inventory_file}"
  }

  triggers = {
    template = data.template_file.inventory.rendered
  }
}
