require 'spec_helper'

describe file('/etc/molecule/example-group2') do
  it { should be_a_file }
  it { should be_owned_by 'root' }
  it { should be_grouped_into 'root' }
  it { should be_mode 644 }
  it { should contain 'molecule example-group2 file' }
end

describe file('/etc/molecule/example-group1') do
  it { should_not exist }
end
