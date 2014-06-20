# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.synced_folder ".", "/vagrant"#, type: "rsync",
#     rsync__exclude: [".git/", ".idea/"]
  config.vm.box = "hashicorp/precise64"
  config.vm.hostname = "malice"

  # For Flask App
  config.vm.network "forwarded_port", guest: 5000, host: 5000, auto_correct: true
  # For RethinkDB Admin Web Interface
  config.vm.network "forwarded_port", guest: 8080, host: 8080, auto_correct: true

  config.vm.provider :aws do |aws, override|
    aws.access_key_id = "YOUR KEY"
    aws.secret_access_key = "YOUR SECRET KEY"
    aws.keypair_name = "KEYPAIR NAME"
    aws.instance_type = "t1.micro"
    aws.tags = {
      'Name' => 'malice',
      'Description' => 'VirusTotal Wannabe',
      'Contact' => 'me'
    }
    aws.ami = "ami-7747d01e"
    override.ssh.username = "ubuntu"
    override.ssh.private_key_path = "PATH TO YOUR PRIVATE KEY"
  end

  config.vm.provider "virtualbox" do |vb|
    # Boot in headless mode
    vb.gui = false
    vb.name = "malice_dev"
    vb.memory = 1024
    vb.cpus = 2

    ## For masterless, mount your file roots file root
    config.vm.synced_folder "install/salt/roots/", "/srv/"#, type: "rsync"
    ## Set your salt configs here
    config.vm.provision :salt do |salt|
      ## Minion config is set to ``file_client: local`` for masterless
      salt.minion_config = "install/salt/minion"
      ## Installs our example formula in "salt/roots/salt"
      salt.verbose = true
      salt.colorize = true
      salt.run_highstate = true
    end
  end

  config.vm.provider "vmware_fusion" do |vmwf, override|
    #override.vm.box_url = "http://files.vagrantup.com/precise64_vmware.box"
    vmwf.vmx["displayName"] = "Malice"
    vmwf.vmx["numvcpus"] = "4"
    vmwf.vmx["memsize"] = "4096"
    ## For masterless, mount your file roots file root
    config.vm.synced_folder "install/salt/roots/", "/srv/"#, type: "rsync"

    ## Set your salt configs here
    config.vm.provision :salt do |salt|
      ## Minion config is set to ``file_client: local`` for masterless
      salt.minion_config = "install/salt/minion"
      ## Installs our example formula in "salt/roots/salt"
      salt.verbose = true
      salt.colorize = true
      salt.run_highstate = true
    end
  end
end
