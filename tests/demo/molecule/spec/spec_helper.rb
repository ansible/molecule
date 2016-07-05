require 'serverspec'
require 'net/ssh'

host = ENV['TARGET_HOST']
ssh_config_files = ['./.vagrant/ssh-config'] + Net::SSH::Config.default_files
options = Net::SSH::Config.for(host, ssh_config_files)
options[:user] ||= 'vagrant'
options[:keys].push("#{Dir.home}/.vagrant.d/insecure_private_key")

set :backend, :ssh
set :host, host
set :ssh_options, options

RSpec.configure do |config|
  config.color = true
  config.tty = true
  config.formatter = :documentation
end
