from buildbot.plugins import *

class XbpsBulkFactory(util.BuildFactory):
    """
    """

    void_packages_repo = 'git://github.com/voidlinux/void-packages.git'
    xbps_bulk_repo = 'git://github.com/voidlinux/xbps-bulk.git'
    step_defaults = dict(logEnviron=False, haltOnFailure=True)

    def __init__(self, *args, **kwargs):
        if 'void_packages_repo' in kwargs:
            self.void_packages_repo = kwargs.pop('void_packages_repo')
        if 'xbps_bulk_repo' in kwargs:
            self.void_packages_repo = kwargs.pop('xbps_bulk_repo')
        steps = self.bootstrap_steps() + self.build_steps()
        return super(XbpsBulkFactory, self).__init__(steps, *args, **kwargs)

    def bootstrap_steps(self):
        return (
            steps.Git(
                progress=True,
                mode='incremental',
                description=['updating xbps-bulk from git'],
                descriptionDone=['xbps-bulk updated'],
                workdir="xbps-bulk",
                repourl=self.xbps_bulk_repo,
                **self.step_defaults),
             steps.Git(
                progress=True,
                workdir="void-packages",
                description=['updating xbps-packages from git'],
                descriptionDone=['xbps-packages updated'],
                repourl=self.void_packages_repo,
                mode='incremental',
                **self.step_defaults),
            steps.ShellCommand(
                description=['Installing bootstrap binary packages'],
                descriptionDone=['xbps-src bootstrap installed'],
                command=[
                    "./../void-packages/xbps-src",
                    # "-N",
                    "-m", util.Property("masterdir"),
                    "-H", util.Property("hostdir"),
                    "binary-bootstrap",
                    util.Property("bootstraparch"),
                    ],
                **self.step_defaults),
            )

    def build_steps(self):
        return (
            steps.ShellCommand(
                description=['cleaning masterdir'],
                descriptionDone=['masterdir cleaned'],
                command=[
                    "./../void-packages/xbps-src",
                    "-m", util.Property("masterdir"),
                    "-H", util.Property("hostdir"),
                    "clean",
                    ],
                **self.step_defaults),
            steps.ShellCommand(
                description=['Updating bootstrap binary packages'],
                descriptionDone=['xbps-src bootstrap updated'],
                command=[
                    "./../void-packages/xbps-src",
                    # "-N",
                    "-m", util.Property("masterdir"),
                    "-H", util.Property("hostdir"),
                    "bootstrap-update",
                    ],
                **self.step_defaults),
            steps.ShellCommand(
                workdir="void-packages",
                description=['finding pkgs'],
                descriptionDone=['found pkgs'],
                command=[
                    "./../xbps-bulk/configure",
                    # "-N",
                    "-a", util.Property("targetarch"),
                    "-d", "../{}".format("void-packages"),
                    "-m", "../{}".format(util.Property("masterdir")),
                    "-h", "../{}".format(util.Property("hostdir")),
                    ],
                **self.step_defaults),
            steps.SetPropertyFromCommand(
                workdir="void-packages",
                property="packages",
                command=[
                    "make", "print_pkgs"
                    ],
                **self.step_defaults),
            steps.ShellCommand(
                description=["building {}".format(util.Property("packages"))],
                descriptionDone=[
                    "finished {}".format(util.Property("packages"))],
                command=[
                    "make",
                    ],
                **self.step_defaults),
            )
