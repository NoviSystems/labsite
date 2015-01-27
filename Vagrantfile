Vagrant.configure("2") do |config|

    config.vm.box = "chef/centos-7.0"

    # disabled the shared folder for all boxes
    config.vm.synced_folder '.', '/vagrant', disabled: true

    config.vm.define "application" do |app|
        app.vm.network :private_network, ip: "192.168.10.20"
    end

    config.vm.define "broker" do |broker|
        broker.vm.network :private_network, ip: "192.168.10.10"
    end

    config.vm.define "database" do |db|
        db.vm.network :private_network, ip: "192.168.10.11"
    end
end