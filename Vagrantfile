# -*- mode: ruby -*-
# vi: set ft=ruby :

$set_environment_variables = <<SCRIPT
tee "/etc/profile.d/javavars.sh" > "/dev/null" <<EOF
export OSNAME=linux
# JAVA home path.
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export JDK=/usr/lib/jvm/java-8-openjdk-amd64
# Jreduce and javaq path.
export PATH=$HOME/.local/bin:$PATH
EOF
SCRIPT

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial64"
  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
   config.vm.synced_folder ".", "/vagrant"

  #
  config.vm.provider "virtualbox" do |vb|
    # Customize the amount of memory on the VM:
    vb.memory = "16000"
    #vb.disksize.size='70GB'
  end
  config.disksize.size='70GB'
  #
  # View the documentation for the provider you are using for more
  # information on available options.

  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.
  config.vm.provision "shell", inline: <<-SHELL
    apt-get update --fix-missing
    apt-get install -y --fix-missing git python3 make openjdk-8-jdk maven jq unzip bc python3-venv gcc libgmp3-dev zlib1g-dev

    curl -sSL https://get.haskellstack.org/ | sh
    stack upgrade --binary-version 1.9.3
  SHELL

  config.vm.provision "shell", inline: $set_environment_variables, run: "always"
end
