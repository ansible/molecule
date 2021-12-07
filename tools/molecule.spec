%global srcname molecule
%global pypiname molecule
%global pkgname python3-%{srcname}
%global forgeurl https://github.com/ansible-community/%{srcname}

Name:    %{pkgname}
Version: 0.0.0
Release: 1%{?dist}
Summary: ...
%forgemeta
URL:       %{forgeurl}
Source:    %{forgesource}
License:   BSD
BuildArch: noarch

BuildRequires: python3-devel
BuildRequires: python3-wheel
BuildRequires: python3-tox
# BuildRequires: python3-tox-current-env

%global _description %{expand:
...
}

%description %{_description}

%py_provides python3-%{srcname}

%prep
%autosetup -p1 -n %{srcname}-%{version}

# generate_buildrequires chokes on tox deps = --editable...
# also that one chokes too:
# pyproject_buildrequires -t

%build
%{pyproject_wheel}

%install
%{pyproject_install}

%pyproject_save_files %{pypiname}

%check
# %%{tox} -e lint,py
# tox macro is broken due to:
# https://github.com/fedora-python/tox-current-env/issues/45
# https://github.com/fedora-python/tox-current-env/issues/46
tox -e system --notest

%files -n python3-%{srcname}
# https://bugzilla.redhat.com/show_bug.cgi?id=2023561
# -f %%{pyproject_files}
/usr/bin/mol
/usr/bin/molecule
%{python3_sitelib}/%{srcname}
%{python3_sitelib}/%{srcname}-*.dist-info
%doc     README.rst
%license LICENSE
