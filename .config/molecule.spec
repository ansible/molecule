# spell-checker:ignore bcond pkgversion buildrequires autosetup PYTHONPATH noarch buildroot bindir sitelib numprocesses
# All tests require Internet access
# to test in mock use:  --enable-network --with check
# to test in a privileged environment use:
#   --with check --with privileged_tests
%bcond_with     check
%bcond_with     privileged_tests

Name:           molecule
Version:        VERSION_PLACEHOLDER
Release:        1%{?dist}
Summary:        Molecule testing framework for Ansible content

License:        MIT
URL:            https://github.com/ansible-community/molecule
Source0:        %{pypi_source}

BuildArch:      noarch

BuildRequires:  pyproject-rpm-macros
BuildRequires:  python%{python3_pkgversion}-build
BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-pip
BuildRequires:  python%{python3_pkgversion}-setuptools
BuildRequires:  python%{python3_pkgversion}-setuptools_scm
BuildRequires:  python%{python3_pkgversion}-wheel
%if %{with check}
# These are required for tests:
BuildRequires:  python%{python3_pkgversion}-pyyaml
BuildRequires:  python%{python3_pkgversion}-pytest
BuildRequires:  python%{python3_pkgversion}-pytest-xdist
BuildRequires:  python%{python3_pkgversion}-libselinux
BuildRequires:  git
%endif
# Named based on fedora 35:
Requires:       ansible-core
Requires:       python3-enrich
Requires:       python3-packaging
Requires:       python3-pyyaml
Requires:       python3-rich

# generate_buildrequires
# pyproject_buildrequires

%description
Molecule provides support for testing with multiple instances, operating
systems and distributions, virtualization providers, test frameworks and
testing scenarios.

%prep
%autosetup


%build
%pyproject_wheel


%install
%pyproject_install


%if %{with check}
%check
PYTHONPATH=%{buildroot}%{python3_sitelib} \
  pytest-3 \
  -v \
  --disable-pytest-warnings \
  --numprocesses=auto \
%if %{with privileged_tests}
  tests
%else
  tests/unit
%endif
%endif


%files
%{python3_sitelib}/molecule/
%{python3_sitelib}/molecule-*.dist-info/
%{_bindir}/molecule
%license LICENSE
%doc docs/* README.md

%changelog
Available at https://github.com/ansible-community/molecule/releases
