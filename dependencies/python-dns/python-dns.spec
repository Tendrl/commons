%global pypi_name dns
%global python_name dnspython

Name:           python-%{pypi_name}
Version:        1.14.0
Release:        1%{?dist}
Summary:        DNS toolkit for Python

License:        Nominum, equivalent to the BSD 2-Clause and MIT
URL:            http://www.dnspython.org
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python-setuptools
BuildRequires:  python2-devel

%if 0%{?fedora}
BuildRequires:  python3-setuptools
BuildRequires:  python3-devel
%endif

%description
dnspython is a DNS toolkit for Python. It supports almost all
record types. It can be used for queries, zone transfers, and dynamic
updates.  It supports TSIG authenticated messages and EDNS0.
dnspython provides both high and low level access to DNS.


%package -n     python2-%{pypi_name}
Summary:        DNS toolkit
%if 0%{?fedora} > 19
%{?python_provide:%python_provide python2-%{pypi_name}}
%endif

%description -n python2-%{pypi_name}
dnspython is a DNS toolkit for Python. It supports almost all
record types. It can be used for queries, zone transfers, and dynamic
updates.  It supports TSIG authenticated messages and EDNS0.
dnspython provides both high and low level access to DNS.


%if 0%{?fedora} > 19
%package -n     python3-%{pypi_name}
Summary:        DNS toolkit
%{?python_provide:%python_provide python3-%{pypi_name}}

%description -n python3-%{pypi_name}
dnspython is a DNS toolkit for Python. It supports almost all
record types. It can be used for queries, zone transfers, and dynamic
updates.  It supports TSIG authenticated messages and EDNS0.
dnspython provides both high and low level access to DNS.
%endif


%prep
%autosetup -n %{name}-%{version}
rm -rf %{pypi_name}.egg-info

%build
%py2_build

%if 0%{?fedora}
%py3_build
%endif

%install
%if 0%{?fedora}
%py3_install
%endif


%py2_install


%files -n python2-%{pypi_name}
%doc README.md LICENSE
%{python2_sitelib}/%{pypi_name}
%{python2_sitelib}/%{python_name}-%{version}-py?.?.egg-info

%if 0%{?fedora}
%files -n python3-%{pypi_name}
%doc README.md LICENSE
%{python3_sitelib}/%{pypi_name}
%{python3_sitelib}/%{python_name}-%{version}-py?.?.egg-info
%endif

%changelog
* Thu Apr 27 2017 Timothy Asir Jeyasingh <tjeyasin@redhat.com> - 1.14.0-1
- Initial package.
