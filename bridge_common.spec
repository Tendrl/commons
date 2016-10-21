%define pkg_name tendrl-bridge-common
%define pkg_version 0.0.1
%define pkg_release 1

Name: %{pkg_name}
Version: %{pkg_version}
Release: %{pkg_release}%{?dist}
BuildArch: noarch
Summary: Common Module for All Bridges
Source0: %{pkg_name}-%{pkg_version}.tar.gz
Group:   Applications/System
License: GPLv2+
Url: https://github.com/Tendrl/bridge_common

BuildRequires: python-devel
BuildRequires: python-setuptools
BuildRequires: python-pbr

Requires: python-pip
Requires: python-pbr
Requires: python-etcd
Requires: python-dateutil
Requires: python-gevent
Requires: python-greenlet
Requires: pytz
Requires: python-oslo-log

%description
Common python module usable by all Tendrl SDS Bridges

%prep
%setup -n %{pkg_name}-%{pkg_version}
# Remove the requirements file to avoid adding into
# distutils requiers_dist config
rm -rf {test-,}requirements.txt

# Remove bundled egg-info
rm -rf %{pkg_name}.egg-info

%build
%{__python} setup.py build

# generate html docs
%if 0%{?rhel}==6
sphinx-1.0-build doc/source html
%else
sphinx-build doc/source html
%endif
# remove the sphinx-build leftovers
rm -rf html/.{doctrees,buildinfo}

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
install -Dm 755 etc/tendrl/tendrl.conf.sample $RPM_BUILD_ROOT/etc/tendrl/tendrl.conf

%post
mkdir /var/log/tendrl >/dev/null 2>&1 || :

%clean
rm -rf $RPM_BUILD_ROOT

%if 0%{?do_test}
%check
%{__python} setup.py test
%endif

%files -f INSTALLED_FILES
%defattr(-,root,root)
%doc html README.rst LICENSE
%{_sysconfdir}/tendrl/tendrl.conf


%changelog
* Mon Oct 17 2016 Timothy Asir Jeyasingh <tjeyasin@redhat.com> - 0.0.1-1
- Initial build.
