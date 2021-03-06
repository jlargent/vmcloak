# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class AdobePdf(Dependency):
    name = "adobepdf"
    default = "9.0.0"
    exes = [
        {
            "version": "9.0.0",
            "url": "http://cuckoo.sh/vmcloak/AdbeRdr90_en_US.exe",
            "sha1": "8faabd08289b9a88023f71136f13fc4bd3290ef0",
        },
        {
            "version": "10.1.4",
            "url": "http://cuckoo.sh/vmcloak/AdbeRdr1014_en_US.exe",
            "sha1": "fe6808d5d11e94dc5581f33ed386ce552f0c84d6",
        },
        {
            "version": "11.0.2",
            "url": "http://cuckoo.sh/vmcloak/AdbeRdr11002_en_US.exe",
            "sha1": "e1d9e57f08e169fb1c925f8ded93e5f5efe5cda3",
        },
        {
            "version": "11.0.3",
            "url": "http://cuckoo.sh/vmcloak/AdbeRdr11003_en_US.exe",
            "sha1": "9c2b6903b000ecf2869e1555bc6e1b287e6176bf",
        },
        {
            "version": "11.0.4",
            "url": "http://cuckoo.sh/vmcloak/AdbeRdr11004_en_US.exe",
            "sha1": "9c295c16d374735bf292ef6c630c9ab392c22500",
        },
        {
            "version": "11.0.6",
            "url": "http://cuckoo.sh/vmcloak/AdbeRdr11006_en_US.exe",
            "sha1": "6a3d5b494b4ed6e11fc7d917afc03eaf05d4a6aa",
        },
        {
            "version": "11.0.7",
            "url": "http://cuckoo.sh/vmcloak/AdbeRdr11007_en_US.exe",
            "sha1": "3e08c3f6daad59f463227590cc438b3906648f5e",
        },
        {
            "version": "11.0.8",
            "url": "http://cuckoo.sh/vmcloak/AdbeRdr11008_en_US.exe",
            "sha1": "3e889258ea2000337bbe180d81317d44f617a292",
        },
        {
            "version": "11.0.9",
            "url": "http://cuckoo.sh/vmcloak/AdbeRdr11009_en_US.exe",
            "sha1": "53b367bff07a63ee07cf1cd090360b75d3fc6bfb",
        },
        {
            "version": "11.0.10",
            "url": "http://cuckoo.sh/vmcloak/AdbeRdr11010_en_US.exe",
            "sha1": "98b2b838e6c4663fefdfd341dfdc596b1eff355c",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\%s" % self.filename)
        self.a.execute(
            "C:\\%s /sAll /msi /norestart /quiet ALLUSERS=1 EULA_ACCEPT=YES" %
            self.filename
        )

        self.a.remove("C:\\%s" % self.filename)

        # add needed registry keys to skip Licence Agreement
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\Software\\WOW6432Node\\"
            "Adobe\\Acrobat Reader\\9.0\\AdobeViewer\" "
        )
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\Software\\WOW6432Node\\"
            "Adobe\\Acrobat Reader\\9.0\\AdobeViewer\" "
            "/v EULA /t REG_DWORD /d 1 /f"
        )
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\Software\\WOW6432Node\\"
            "Adobe\\Acrobat Reader\\9.0\\AdobeViewer\" "
            "/v Launched /t REG_DWORD /d 1 /f"
        )

        # man : https://www.adobe.com/devnet-docs/acrobatetk/tools/PrefRef/Windows/
        # we don't care about updates really
        self.a.execute(
            "reg add \"HKEY_CURRENT_USER\\Software\\Adobe\\"
            "Acrobat Reader\\9.0\\AVGeneral\" "
            "/v bCheckForUpdatesAtStartup /t REG_DWORD /d 0 /f"
        )

        # allow URL access
        self.a.execute(
            "reg add \"HKEY_CURRENT_USER\\Software\\Adobe\\"
            "Acrobat Reader\\9.0\\TrustManager\\cDefaultLaunchURLPerms\" "
        )
        self.a.execute(
            "reg add \"HKEY_CURRENT_USER\\Software\\Adobe\\"
            "Acrobat Reader\\9.0\\TrustManager\\cDefaultLaunchURLPerms\" "
            "/v iURLPerms /t REG_DWORD /d 2 /f"
        )

        # FIXME: really needed ?
        self.a.execute(
            "reg add \"HKEY_CURRENT_USER\\Software\\Adobe\\"
            "Acrobat Reader\\9.0\\Security\\cDigSig\\cCustomDownload\" "
            "/v bLoadSettingsFromURL /t REG_DWORD /d 0 /f"
        )

class Adobe9(AdobePdf, Dependency):
    """Backwards compatibility."""
    name = "adobe9"
