Name: tendrl-commons
Version: 1.6.3
Release: 13%{?dist}
BuildArch: noarch
Summary: Common lib for Tendrl sds integrations and node-agent
Source0: %{name}-%{version}.tar.gz
License: LGPLv2+
URL: https://github.com/Tendrl/commons

BuildRequires: python3-pytest
BuildRequires: python3-devel
BuildRequires: python3-six
BuildRequires: systemd

Requires: ansible >= 2.5
Requires: python3-maps
Requires: python3-dateutil
Requires: python3-dns
Requires: python3-etcd
Requires: python3-six
Requires: python3-ruamel-yaml
Requires: pytz
Requires: python3-psutil
Requires: python3-IPy
Requires: python3-pyasn1 <= 0.1.9

%description
Common library for tendrl

%prep
%setup

# Remove bundled egg-info
rm -rf %{name}.egg-info

%build
%{__python3} setup.py build

%install
%{__python3} setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%check
py.test -v tendrl/commons/tests || :

%files -f INSTALLED_FILES
%doc README.rst
%license LICENSE

%changelog
* Mon Mar 16 2020 Timothy Asir Jeyasingh <tjeyasin@redhat.com> - 1.6.3-13
- Python3 package conversion

* Tue Aug 14 2018 Shubhendu Tripathi <shtripat@redhat.com> - 1.6.3-11
- Bugfixes (https://github.com/Tendrl/commons/milestone/11)

* Fri Jul 27 2018 Shubhendu Tripathi <shtripat@redhat.com> - 1.6.3-10
- Bugfixes (https://github.com/Tendrl/commons/milestone/10)

* Sat Jul 14 2018 Rohan Kanade <rkanade@redhat.com> - 1.6.3-9
- Bugfixes (https://github.com/Tendrl/commons/milestone/10)

* Wed Jul 04 2018 Rohan Kanade <rkanade@redhat.com> - 1.6.3-8
- Bugfixes (https://github.com/Tendrl/commons/milestone/10)

* Mon Jun 18 2018 Shubhendu Tripathi <shtripat@redhat.com> - 1.6.3-7
- Bugfixes (https://github.com/Tendrl/commons/milestone/9)

* Thu May 31 2018 Rohan Kanade <rkanade@redhat.com> - 1.6.3-6
- Bugfixes (https://github.com/Tendrl/commons/milestone/8)

* Wed May 16 2018 Rohan Kanade <rkanade@redhat.com> - 1.6.3-5
- Bugfixes (https://github.com/Tendrl/commons/milestone/7)

* Fri May 04 2018 Rohan Kanade <rkanade@redhat.com> - 1.6.3-4
- Bugfixes (https://github.com/Tendrl/commons/milestone/7)

* Tue Apr 24 2018 Rohan Kanade <rkanade@redhat.com> - 1.6.3-3
- Bugfixes (https://github.com/Tendrl/commons/milestone/6)

* Fri Apr 20 2018 Rohan Kanade <rkanade@redhat.com> - 1.6.3-2
- Bugfixes (https://github.com/Tendrl/commons/milestone/6)

* Wed Apr 18 2018 Rohan Kanade <rkanade@redhat.com> - 1.6.3-1
- Support gluster nodes/bricks with fqdn, IP and short names
- Serialize/deserialize Tendrl objects
- Support for Cluster short names/alias

* Thu Mar 22 2018 Rohan Kanade <rkanade@redhat.com> - 1.6.2-1
- Bugfixes (https://github.com/Tendrl/commons/milestone/4)

* Wed Mar 07 2018 Rohan Kanade <rkanade@redhat.com> - 1.6.1-1
- Auto expand clusters managed by Tendrl

* Sat Feb 17 2018 Rohan Kanade <rkanade@redhat.com> - 1.6.0-1
- API to un-manage clusters managed by Tendrl

* Fri Feb 02 2018 Rohan Kanade <rkanade@redhat.com> - 1.5.5-1
- Move gluster.event_utils to commons
- Fix geo-rep classification
- Raise alert when node goes down, when cluster health changes

* Mon Dec 11 2017 Rohan Kanade <rkanade@redhat.com> - 1.5.4-9
- Add dependency on python-IPy, python-dns

* Wed Dec 06 2017 Rohan Kanade <rkanade@redhat.com> - 1.5.4-8
- Bugfixes

* Tue Dec 05 2017 Rohan Kanade <rkanade@redhat.com> - 1.5.4-7
- Bugfixes

* Thu Nov 30 2017 Rohan Kanade <rkanade@redhat.com> - 1.5.4-6
- Fix import cluster hard coded tendrl-gluster-integration sync_interval

* Mon Nov 27 2017 Rohan Kanade <rkanade@redhat.com> - 1.5.4-5
- Fix alert time-stamp when alert status changes

* Tue Nov 21 2017 Rohan Kanade <rkanade@redhat.com> - 1.5.4-4
- Bugfixes-3 tendrl-commons v1.5.4

* Sat Nov 18 2017 Rohan Kanade <rkanade@redhat.com> - 1.5.4-3
- Bugfixes-2 tendrl-commons v1.5.4

* Fri Nov 10 2017 Rohan Kanade <rkanade@redhat.com> - 1.5.4-2
- Bugfixes tendrl-commons v1.5.4

* Thu Nov 02 2017 Rohan Kanade <rkanade@redhat.com> - 1.5.4-1
- Release tendrl-commons v1.5.4

* Thu Oct 12 2017 Rohan Kanade <rkanade@redhat.com> - 1.5.3-1
- Release tendrl-commons v1.5.3

* Fri Sep 15 2017 Rohan Kanade <rkanade@redhat.com> - 1.5.2-1
- Release tendrl-commons v1.5.2

* Fri Aug 25 2017 Rohan Kanade <rkanade@redhat.com> - 1.5.1-1
- Release tendrl-commons v1.5.1

* Fri Aug 04 2017 Rohan Kanade <rkanade@redhat.com> - 1.5.0-1
- Release tendrl-commons v1.5.0

* Mon Jun 19 2017 Rohan Kanade <rkanade@redhat.com> - 1.4.2-1
- Release tendrl-commons v1.4.2

* Sun Jun 11 2017 Rohan Kanade <rkanade@redhat.com> - 1.4.1-2
- Fixes https://github.com/Tendrl/commons/issues/587

* Thu Jun 08 2017 Rohan Kanade <rkanade@redhat.com> - 1.4.1-1
- Release tendrl-commons v1.4.1

* Fri Jun 02 2017 Rohan Kanade <rkanade@redhat.com> - 1.4.0-1
- Release tendrl-commons v1.4.0

* Thu May 18 2017 Rohan Kanade <rkanade@redhat.com> - 1.3.0-1
- Release tendrl-commons v1.3.0

* Tue Apr 18 2017 Rohan Kanade <rkanade@redhat.com> - 1.2.3-1
- Release tendrl-commons v1.2.3

* Sat Apr 01 2017 Rohan Kanade <rkanade@redhat.com> - 1.2.2-1
- Release tendrl-commons v1.2.2

* Tue Dec 06 2016 Martin Bukatovič <mbukatov@redhat.com> - 0.0.1-2
- Fixed https://github.com/Tendrl/commons/issues/72

* Mon Oct 17 2016 Timothy Asir Jeyasingh <tjeyasin@redhat.com> - 0.0.1-1
- Initial build.
