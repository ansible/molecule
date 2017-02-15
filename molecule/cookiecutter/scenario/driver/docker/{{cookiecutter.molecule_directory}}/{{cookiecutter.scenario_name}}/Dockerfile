FROM centos:7

RUN yum makecache fast && yum update -y && yum install -y sudo yum-plugin-ovl && sed -i 's/^plugins=0$/plugins=1/g' /etc/yum.conf && yum clean all
