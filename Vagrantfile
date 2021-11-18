# https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners#supported-runners-and-hardware-resources
Vagrant.configure("2") do |config|
  config.vbguest.installer_options = { allow_kernel_upgrade: true }
  config.vm.provider "virtualbox" do |v|
    v.memory = 7168
    v.cpus = 2
    v.customize ["modifyvm", :id, "--uart1", "0x3F8", "4"]
    v.customize ["modifyvm", :id, "--uartmode1", "file", File::NULL]
  end

  config.vm.define "focal" do |focal|
    focal.vm.box = "ubuntu/focal64"
    focal.vm.hostname = "focal"
    focal.vm.provision "shell", path: "./tools/vagrant-test-runner.sh"
  end

  config.vm.define "bullseye" do |bullseye|
    bullseye.vm.box = "debian/bullseye64"
    bullseye.vm.hostname = "bullseye"
    bullseye.vm.provision "shell", path: "./tools/vagrant-test-runner.sh"
  end

  config.vm.define "fedora" do |fedora|
    fedora.vm.box = "fedora/35-cloud-base"
    fedora.vm.hostname = "fedora"
    fedora.vm.provision "shell", path: "./tools/vagrant-test-runner.sh"
  end
end
