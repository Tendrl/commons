Name: tendrl-commons
Version: 1.2.2
Release: 1%{?dist}
BuildArch: noarch
Summary: Common lib for Tendrl sds integrations and node-agent
Source0: %{name}-%{version}.tar.gz
License: LGPLv2+
URL: https://github.com/Tendrl/commons

BuildRequires: ansible >= 2.2
BuildRequires: pytest
BuildRequires: python2-devel
BuildRequires: python-mock
BuildRequires: python-six
BuildRequires: systemd

Requires: ansible >= 2.2
Requires: python-maps
Requires: python-dateutil
Requires: python-dns
Requires: python-etcd
Requires: systemd-python
Requires: python-urllib3
Requires: python-six
Requires: python-docutils
Requires: python-ruamel-yaml
Requires: pytz
Requires: python-psutil
Requires: python-gevent


%description
Common lib for Tendrl sds integrations and node-agent

%prep
%setup

# Remove bundled egg-info
rm -rf %{name}.egg-info

%build
%{__python} setup.py build

%install
%{__python} setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%check

%files -f INSTALLED_FILES
%doc README.rst
%license LICENSE

%changelog
* Sat Apr 01 2017 Rohan Kanade <rkanade@redhat.com> - 1.2.2-1
- Release tendrl-commons v1.2.2

* Tue Dec 06 2016 Martin Bukatovič <mbukatov@redhat.com> - 0.0.1-2
- Fixed https://github.com/Tendrl/commons/issues/72

* Mon Oct 17 2016 Timothy Asir Jeyasingh <tjeyasin@redhat.com> - 0.0.1-1
- Initial build.
