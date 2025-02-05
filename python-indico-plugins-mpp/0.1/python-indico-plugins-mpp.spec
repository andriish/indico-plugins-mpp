%global srcname indico-plugins-mpp
Name:           python-%{srcname}
Version:        0.1
Release:        1%{?dist}
Summary:        Indico package

License:        MIT
URL:            https://getindico.io/
Source0:        https://github.com/andriish/indico-plugins-mpp/archive/refs/heads/master.zip
BuildArch:      noarch

%define filesinplugin() \
%%files -n python3-indico-%1-plugin \
%{python3_sitelib}/indico_%1/* \
%{python3_sitelib}/indico_plugin_%1-3.3.dev0-info/*

%define iplugin()  \
%%package -n python3-indico-%1-plugin \
Summary:        Indico plugin %1  \
%%description -n python3-indico-%1-plugin \
Indico plugin %1 


%global _description %{expand:
Indico event management system.
}
%description %_description


%iplugin mpppanel

%prep
%autosetup  -n indico-plugins-mpp-master

%{__python3} -m pip install ./mpppanel --root=%{buildroot} --no-dependencies


%filesinplugin mpppanel




%changelog
* Mon Apr 15 2024 Andrii Verbytskyi andrii.verbytskyi@mpp.mpg.de> - 3.3.1
- Version 3.3.1 
