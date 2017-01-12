Name: tendrl-commons
Version: 1.1
Release: 2%{?dist}
BuildArch: noarch
Summary: Common module for Tendrl bridges and node_agent
Source0: %{name}-%{version}.tar.gz
License: LGPLv2+
URL: https://github.com/Tendrl/commons

BuildRequires: ansible >= 2.2
BuildRequires: pytest
BuildRequires: python2-devel
BuildRequires: python-mock
BuildRequires: python-six
BuildRequires: systemd
BuildRequires: python-yaml

Requires: ansible >= 2.2
Requires: python-dateutil
Requires: python-dns
Requires: python-etcd
Requires: systemd-python
Requires: python-urllib3
Requires: python-six
Requires: python-docutils
Requires: python-yaml

%description
Common python module usable by all Tendrl SDS Bridges

%prep
%setup

# Remove bundled egg-info
rm -rf %{name}.egg-info

%build
%{__python} setup.py build

%install
%{__python} setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
install -m  0755 --directory $RPM_BUILD_ROOT%{_var}/log/tendrl/commons
install -Dm 644 etc/tendrl/tendrl.conf.sample $RPM_BUILD_ROOT%{_datadir}/tendrl/commons/tendrl.conf.sample
install -Dm 644 etc/samples/logging.yaml.timedrotation.sample $RPM_BUILD_ROOT%{_sysconfdir}/tendrl/commons_logging.yaml
install -Dm 644 etc/samples/*.sample $RPM_BUILD_ROOT%{_datadir}/tendrl/commons/.

%check
py.test -v tendrl/commons/tests || :

%files -f INSTALLED_FILES
%dir %{_var}/log/tendrl/commons
%dir %{_datadir}/tendrl/commons
%dir %{_sysconfdir}/tendrl
%doc README.rst
%license LICENSE
%{_datadir}/tendrl/commons/
%{_datarootdir}/tendrl/commons/tendrl.conf.sample
%config(noreplace) %{_sysconfdir}/tendrl/commons_logging.yaml

%changelog
* Tue Dec 06 2016 Martin Bukatovič <mbukatov@redhat.com> - 0.0.1-2
- Fixed https://github.com/Tendrl/commons/issues/72

* Mon Oct 17 2016 Timothy Asir Jeyasingh <tjeyasin@redhat.com> - 0.0.1-1
- Initial build.
