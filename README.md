# DIRACOS

[![pipeline status](https://gitlab.cern.ch/CLICdp/iLCDirac/DIRACOS/badges/master/pipeline.svg)](https://gitlab.cern.ch/CLICdp/iLCDirac/DIRACOS/pipelines)

DIRACOS aims at bringing in one archive all the dependencies needed by DIRAC to run Agents, Services and clients. It is not intended to perform interactive tasks (debugging, file editing, etc). We are aware than some "basic" tools won't work (less, emacs, etc). They won't be fixed.


- [ Principle](docs/0_concepts.md#principle)
  * [ How it works](docs/0_concepts.md#how-it-works)
    + [ Bootstrap issue](docs/0_concepts.md#bootstrap-issue)
    + [ About EPEL repository](docs/0_concepts.md#about-epel-repository)
    + [ About links](docs/0_concepts.md#about-links)
    + [ About dependencies](docs/0_concepts.md#about-dependencies)
  * [ Supported platforms](docs/0_concepts.md#supported-platforms)
    + [ Trick](docs/0_concepts.md#trick)
- [ Building RPMs](docs/10_RPMs.md#building-rpms)
  * [ Patching the sources](docs/10_RPMs.md#patching-the-sources)
  * [ Altering the normal build workflow](docs/10_RPMs.md#altering-the-normal-build-workflow)
  * [ Caching mechanism](docs/10_RPMs.md#caching-mechanism)
  * [ Adding an RPM package](docs/10_RPMs.md#adding-an-rpm-package)
- [ Python packages](docs/20_pythonPackages.md#python-packages)
  * [ Adding a python package](docs/20_pythonPackages.md#adding-a-python-package)
- [ Generate a new diracos](docs/30_generatingDIRACOS.md#generate-a-new-diracos)
  * [ Initial setup](docs/30_generatingDIRACOS.md#initial-setup)
  * [ Configuration files](docs/30_generatingDIRACOS.md#configuration-files)
  * [ Building everything](docs/30_generatingDIRACOS.md#building-everything)
  * [ Build the python modules](docs/30_generatingDIRACOS.md#build-the-python-modules)
  * [ Bundle DIRACOS](docs/30_generatingDIRACOS.md#bundle-diracos)
  * [ Get your bundle](docs/30_generatingDIRACOS.md#get-your-bundle)
  * [ Test it !](docs/30_generatingDIRACOS.md#test-it-!)
- [ Configuration Grammar](docs/40_grammar.md#configuration-grammar)
  * [ rpmBuild section](docs/40_grammar.md#rpmbuild-section)
    + [ Package and PackageGroup](docs/40_grammar.md#package-and-packagegroup)
      + [ Mandatory parameters](docs/40_grammar.md#mandatory-parameters)
      + [ Optional parameters](docs/40_grammar.md#optional-parameters)
  * [ Other sections and options](docs/40_grammar.md#other-sections-and-options)
- [ Troubleshoot](docs/50_troubleshoot.md#troubleshoot)
  * [ Error `Requires: python(abi) = 2.6`](docs/50_troubleshoot.md#error-requires-pythonabi-26)
  * [ Build is failing for broken rpm dependencies](docs/50_troubleshoot.md#build-is-failing-for-broken-rpm-dependencies)
  * [ Script fails for missing python module](docs/50_troubleshoot.md#script-fails-for-missing-python-module)
  * [ Issue with rpath](docs/50_troubleshoot.md#issue-with-rpath)
  * [ CentOS7](docs/50_troubleshoot.md#centos7)
  * [ Symlinks](docs/50_troubleshoot.md#symlinks)
  * [ Singularity](docs/50_troubleshoot.md#singularity)
  * [ About manualDependencies](docs/50_troubleshoot.md#about-manualdependencies)
  * [ LDD check failing](docs/50_troubleshoot.md#ldd-check-failing)
- [ Test DIRACOS as a User](docs/60_useDIRACOS.md#test-diracos-as-a-user)
- [ Make a new release](docs/70_release.md#make-a-new-release)
  * [ Versioning](docs/70_release.md#versioning)
  * [ Manual execution of steps](docs/70_release.md#manual-execution-of-steps)
    + [ Get list of PRs and update release notes](docs/70_release.md#get-list-of-prs-and-update-release-notes)
    + [ Make a release branch](docs/70_release.md#make-a-release-branch)
    + [ Fix the pip requirements versions](docs/70_release.md#fix-the-pip-requirements-versions)
      + [ About git packages](docs/70_release.md#about-git-packages)
    + [ Build DIRACOS](docs/70_release.md#build-diracos)
    + [ Deploy the archive](docs/70_release.md#deploy-the-archive)
  * [ Automatic generation of a release](docs/70_release.md#automatic-generation-of-a-release)
    + [ New Release](docs/70_release.md#new-release)
    + [ Test Build](docs/70_release.md#test-build)
- [ Extending DIRACOS](docs/80_extendingDIRACOS.md#extending-diracos)
  * [ Requesting a package to be added in DIRACOS](docs/80_extendingDIRACOS.md#requesting-a-package-to-be-added-in-diracos)
  * [ Adding pure python packages](docs/80_extendingDIRACOS.md#adding-pure-python-packages)
    + [ Initial setup](docs/80_extendingDIRACOS.md#initial-setup)
    + [ Configuration files](docs/80_extendingDIRACOS.md#configuration-files)
    + [ Building the extension](docs/80_extendingDIRACOS.md#building-the-extension)
  * [ Adding RPM packages or compiled python packages](docs/80_extendingDIRACOS.md#adding-rpm-packages-or-compiled-python-packages)
  * [ Removing packages](docs/80_extendingDIRACOS.md#removing-packages)
  * [ Using DIRACOS extension in your DIRAC extension](docs/80_extendingDIRACOS.md#using-diracos-extension-in-your-dirac-extension)




Note: summary generated with
```
# the pages are sorted thanks to the numbers in front
for doc in $(find docs -type f -name '*.md'| sort -n );
do grep '^#' $doc | while read title;
   do
     # The text is the title, with an indentation level depending on the depth, with square brackets
     linkText=$(echo $title | sed -E -e 's/#{4}(.*)/      + [\1]/g' -e 's/#{3}(.*)/    + [\1]/g' -e 's/#{2}(.*)/  * [\1]/g' -e 's/#{1}(.*)/- [\1]/g')
     # The anchor is the title, all lowercase, without special char, with '-' instead of space
     anchor=$(echo $title | tr '[A-Z]' '[a-z]' |   sed -E -e 's/#+ +//g' -e 's/ /-/g');
     echo "$linkText($doc#$anchor)";
   done;
done

```

## Disclaimer
DIRACOS is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. We are aiming at supporting SLC6 and CC7, whilst we test also on other platforms we do not provide support for those.
