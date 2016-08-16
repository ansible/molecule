require 'docker'
require 'serverspec'

host = ENV['TARGET_HOST']

set :backend, :docker
set :host, host

RSpec.configure do |config|
  config.color = true
  config.tty = true
  config.formatter = :documentation
  config.before(:suite) do
    set :docker_container, host
  end
end
