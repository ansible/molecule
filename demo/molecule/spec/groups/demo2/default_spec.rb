require 'spec_helper'

describe file('/etc/molecule/demo2') do
  it { should be_a_file }
  it { should be_owned_by 'root' }
  it { should be_grouped_into 'root' }
  it { should be_mode 644 }
  it { should contain 'molecule demo2 file' }
end

describe file('/etc/molecule/demo1') do
  it { should_not exist }
end
