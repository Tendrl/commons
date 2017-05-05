%define name python-etcd
%define version 0.4.5
%define unmangled_version 0.4.5
%define unmangled_version 0.4.5
%define release 1

Summary: A python client for etcd
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: MIT
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Jose Plana <jplana@gmail.com>
Url: http://github.com/jplana/python-etcd

BuildRequires: pytest
BuildRequires: python2-devel

Requires: python-urllib3
Requires: python-dns >= 1.13.0

%description
python-etcd documentation
A python client for Etcd https://github.com/coreos/etcd
Official documentation: http://python-etcd.readthedocs.org/

%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
