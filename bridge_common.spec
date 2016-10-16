%define pkg_name bridge_common
%define pkg_version @VERSION@
%define pkg_release 1

Name: %{pkg_name}
Version: %{pkg_version}
Release: %{pkg_release}%{?dist}
BuildArch: noarch
Summary: Common Module for All Bridges
Source0: %{pkg_name}-%{pkg_version}.tar.gz
Group:   Applications/System
License: GPLv2+
#Url: https://github.com/Tendrl/bridge_common

#BuildRoot: %{_tmppath}/%{pkg_name}-%{pkg_version}-%{pkg_release}-buildroot

BuildRequires: python-devel
BuildRequires: python-setuptools
BuildRequires: gcc, git

Requires: python-pip, gcc, git

%description
Common python module usable by all Tendrl SDS Bridges

%prep
%setup -n %{pkg_name}-%{pkg_version}

%build
python setup.py build

%install
rm -rf $RPM_BUILD_ROOT
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
install -Dm 755 etc/tendrl/tendrl.conf.sample $RPM_BUILD_ROOT/etc/tendrl/tendrl.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv bridge_common
pip install 'virtualenv'
pip install 'virtualenvwrapper'
pip install 'python-etcd'
pip install 'pbr'
pip install 'python-dateutil==2.2'
pip install 'gevent>=1.0'
pip install 'greenlet>=0.3.2'
pip install 'pytz'
pip install 'oslo.log>=3.15.0'

%files -f INSTALLED_FILES
%defattr(-,root,root)
%attr(0755, root, root) /etc/tendrl/tendrl.conf

#%defattr(-,root,root,-)
%doc

%changelog
* Mon Oct 17 2016 Timothy Asir Jeyasingh <tjeyasin@redhat.com> - 0.0.1-1
- Initial build.
