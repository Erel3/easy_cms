terraform { required_version = ">= 0.13.0" }

provider "aws" { region = var.AWS_DEFAULT_REGION }


## Virtual private cloud
resource "aws_vpc" "vpc" {
  cidr_block = var.aws_vpc_cidr_block

  tags = merge(var.default_tags, tomap({
    "Name"= "${var.project_name}-vpc"
  }))
}

resource "aws_subnet" "vpc-public-subnet" {
  vpc_id            = aws_vpc.vpc.id
  availability_zone = data.aws_availability_zones.available.names[0]
  cidr_block        = var.aws_vpc_cidr_block

  tags = merge(var.default_tags, tomap({
    "Name"= "${var.project_name}-public"
  }))
}

resource "aws_internet_gateway" "vpc-internetgw" {
  vpc_id = aws_vpc.vpc.id

  tags = merge(var.default_tags, tomap({
    "Name"= "${var.project_name}-internetgw"
  }))
}

resource "aws_route_table" "routetable-public" {
  vpc_id = aws_vpc.vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.vpc-internetgw.id
  }

  tags = merge(var.default_tags, tomap({
    "Name"= "${var.project_name}-routetable-public"
  }))
}

resource "aws_route_table_association" "routetable-public" {
  subnet_id      = aws_subnet.vpc-public-subnet.id
  route_table_id = aws_route_table.routetable-public.id
}

## Security Groups
resource "aws_security_group" "sec-gr" {
  name   = "${var.project_name}-securitygroup"
  vpc_id = aws_vpc.vpc.id

  tags = merge(var.default_tags, tomap({
    "Name"= "${var.project_name}-securitygroup"
  }))
}
resource "aws_security_group_rule" "allow-all-egress" {
  type              = "egress"
  from_port         = 0
  to_port           = 65535
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.sec-gr.id
}
resource "aws_security_group_rule" "allow-ssh-connections" {
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "TCP"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.sec-gr.id
}
resource "aws_security_group_rule" "allow-http" {
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "TCP"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.sec-gr.id
}
resource "aws_security_group_rule" "allow-https" {
  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "TCP"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.sec-gr.id
}
resource "aws_security_group_rule" "allow-all-local-ingress" {
  type              = "ingress"
  from_port         = 0
  to_port           = 65535
  protocol          = "TCP"
  cidr_blocks       = [var.aws_vpc_cidr_block]
  security_group_id = aws_security_group.sec-gr.id
}



# Create EC2 Instances
resource "aws_instance" "database" {
  ami               = data.aws_ami.distro.id
  instance_type     = var.aws_ec2_db_type
  availability_zone = data.aws_availability_zones.available.names[0]
  subnet_id         = aws_subnet.vpc-public-subnet.id
  associate_public_ip_address = true
  root_block_device {
    volume_type = "io2"
    volume_size = 100
    iops = 50000
  }

  vpc_security_group_ids = [aws_security_group.sec-gr.id]

  key_name = var.AWS_SSH_KEY_NAME

  tags = merge(var.default_tags, tomap({
    "Name"= "${var.project_name}-database",
    "Cluster"= var.project_name,
    "Role"= "database"
  }))
}

resource "aws_instance" "loadbalancer" {
  ami               = data.aws_ami.distro.id
  instance_type     = var.aws_ec2_lb_type
  availability_zone = data.aws_availability_zones.available.names[0]
  subnet_id         = aws_subnet.vpc-public-subnet.id
  root_block_device {
    volume_type = "gp3"
    volume_size = 50
  }

  vpc_security_group_ids = [aws_security_group.sec-gr.id]

  key_name = var.AWS_SSH_KEY_NAME

  tags = merge(var.default_tags, tomap({
    "Name"= "${var.project_name}-loadbalancer",
    "Cluster"= var.project_name,
    "Role"= "loadbalancer"
  }))
}

resource "aws_instance" "webserver" {
  ami               = data.aws_ami.distro.id
  instance_type     = var.aws_ec2_ws_type
  count             = var.awc_ec2_ws_count
  availability_zone = data.aws_availability_zones.available.names[0]
  subnet_id         = aws_subnet.vpc-public-subnet.id
  associate_public_ip_address = true
  root_block_device {
    volume_type = "gp3"
    volume_size = 50
  }

  vpc_security_group_ids = [aws_security_group.sec-gr.id]

  key_name = var.AWS_SSH_KEY_NAME

  tags = merge(var.default_tags, tomap({
    "Name"= "${var.project_name}-worker-${count.index}",
    "Cluster"= var.project_name,
    "Role"= "worker-${count.index}"
  }))
}

resource "aws_instance" "worker" {
  ami               = data.aws_ami.distro.id
  instance_type     = var.aws_ec2_wk_type
  count             = var.awc_ec2_wk_count
  availability_zone = data.aws_availability_zones.available.names[0]
  subnet_id         = aws_subnet.vpc-public-subnet.id
  associate_public_ip_address = true
  root_block_device {
    volume_type = "gp3"
    volume_size = 50
  }

  vpc_security_group_ids = [aws_security_group.sec-gr.id]

  key_name = var.AWS_SSH_KEY_NAME

  tags = merge(var.default_tags, tomap({
    "Name"= "${var.project_name}-worker-${count.index}",
    "Cluster"= var.project_name,
    "Role"= "worker-${count.index}"
  }))
}

resource "aws_eip" "elastic-ip" {
  instance = aws_instance.loadbalancer.id
  domain   = "vpc"
}

# Create Hosts File
data "template_file" "inventory" {
  template = file("${path.module}/templates/hosts.py.tpl")

  vars = {
    ip_db = format("{\"ip\": \"%s\", \"workers\": 0, \"db\": True, \"lb\": False, \"cws\": False, \"aws\": False, \"rws\": False}", aws_instance.database.public_ip)
    ip_lb = format("{\"ip\": \"%s\", \"workers\": 0, \"db\": False, \"lb\": True, \"cws\": False, \"aws\": True, \"rws\": True}", aws_eip.elastic-ip.public_ip)
    ip_ws = join(",\n", formatlist("{\"ip\": \"%s\", \"workers\": 0, \"db\": False, \"lb\": False, \"cws\": True, \"aws\": False, \"rws\": False}", aws_instance.webserver.*.public_ip))
    ip_wk  = join(",\n", formatlist("{\"ip\": \"%s\", \"workers\": 2, \"db\": False, \"lb\": False, \"cws\": False, \"aws\": False, \"rws\": False}", aws_instance.worker.*.public_ip))
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
