Name: tendrl-common
Version: 0.0.1
Release: 1%{?dist}
BuildArch: noarch
Summary: Common Module for all Bridges
Source0: %{name}-%{version}.tar.gz
License: LGPLv2+
URL: https://github.com/Tendrl/bridge_common

BuildRequires: pytest
BuildRequires: python2-devel
BuildRequires: python-mock
BuildRequires: python-six
BuildRequires: systemd
BuildRequires: python-yaml

Requires: python-dateutil
Requires: python-dns
Requires: python-etcd
Requires: systemd-python
Requires: python-urllib3

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
install -m  644 --directory $RPM_BUILD_ROOT%{_var}/log/tendrl/common
install -Dm 644 etc/tendrl/tendrl.conf.sample $RPM_BUILD_ROOT%{_datadir}/tendrl/commons/tendrl.conf.sample
install -Dm 644 etc/samples/logging.yaml.timedrotation.sample $RPM_BUILD_ROOT%{_sysconfdir}/tendrl/common_logging_yaml
install -Dm 644 etc/samples/*.sample $RPM_BUILD_ROOT%{_datadir}/tendrl/commons/.

%check
#py.test -v tendrl/common/tests

%files -f INSTALLED_FILES
%dir %{_var}/log/tendrl/common
%dir %{_datadir}/tendrl/commons
%dir %{_sysconfdir}/tendrl
%doc README.rst
%license LICENSE
%{_datadir}/tendrl/commons/
%{_datarootdir}/tendrl/commons/tendrl.conf.sample
%{_sysconfdir}/tendrl/common_logging_yaml

%changelog
* Mon Oct 17 2016 Timothy Asir Jeyasingh <tjeyasin@redhat.com> - 0.0.1-1
- Initial build.
