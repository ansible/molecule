require 'spec_helper'

describe file('/etc/molecule') do
  it { should be_a_file }
  it { should be_owned_by 'root' }
  it { should be_grouped_into 'root' }
  it { should be_mode 644 }
  it { should contain 'molecule test file' }
end
