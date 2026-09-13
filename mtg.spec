%define debug_package %{nil}

Name:           mtg
Version:        2.2.8
Release:        1%{?dist}
Summary:        Highly opinionated MTPROTO proxy for Telegram

License:        MIT
URL:            https://github.com/9seconds/mtg
Source0:        https://github.com/9seconds/mtg/archive/v%{version}/%{name}-%{version}.tar.gz

# $ GOPROXY=https://proxy.golang.org go mod vendor -v
# Contains mtg-%{version}/vendor/*.
Source1:    %{name}-%{version}.go-mod-vendor.tar.xz

Source2:    mtg.service
Source3:    mtg

%{?systemd_requires}
BuildRequires:  systemd
BuildRequires:  golang >= 1.26

Provides: user(%{name})
Provides: group(%{name})


%description
Highly-opinionated (ex-bullshit-free) MTPROTO proxy for Telegram.


%prep
%setup -q -D -T -b0 -n %{name}-%{version}
%setup -q -D -T -b1 -n %{name}-%{version}


%build
export PKGNAME="%{name}"
export PKGVER="%{version}"

BUILD_ID=$(head -c20 /dev/urandom | od -An -tx1 | tr -d ' \n')
go build -mod=vendor -v \
        -ldflags "-B 0x${BUILD_ID}"


%install
install -m 0755 -D mtg %{buildroot}/%{_bindir}/%{name}
install -m 0644 -D example.config.toml %{buildroot}/%{_sysconfdir}/%{name}/example.config.toml
install -m 0644 -D %{SOURCE2} %{buildroot}/%{_unitdir}/%{name}.service
install -m 0640 -D %{SOURCE3} %{buildroot}%{_sysconfdir}/sysconfig/%{name}


%files
%{_bindir}/%{name}
%dir %{_sysconfdir}/%{name}
%attr(0640,root,%{name}) %{_sysconfdir}/%{name}/example.config.toml
%{_unitdir}/%{name}.service
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}


%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
        useradd -r -s /sbin/nologin -d %{_sysconfdir}/%{name} -M \
        -c 'mtg - Highly opinionated MTPROTO proxy for Telegram' -g %{name} %{name}
exit 0


%post
%systemd_post %{name}.service


%preun
%systemd_preun %{name}.service


%postun
%systemd_postun_with_restart %{name}.service
