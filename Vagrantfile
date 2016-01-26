Vagrant.configure("2") do |config|

    config.vm.box = "bento/centos-7.2"
    config.ssh.insert_key = false
    config.ssh.forward_agent = true

    # disabled the shared folder for all boxes
    config.vm.synced_folder '.', '/vagrant', disabled: true

    config.vm.define "application" do |app|
        app.vm.synced_folder '.', '/home/vagrant/labsite'
        app.vm.network :private_network, ip: "192.168.10.20"
    end

    config.vm.define "services" do |services|
        services.vm.network :private_network, ip: "192.168.10.10"
    end
end
