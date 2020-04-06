DIRACOS
=======

|pipeline status|

DIRACOS aims at bringing in one archive all the dependencies needed by
DIRAC to run Agents, Services and clients. It is not intended to perform
interactive tasks (debugging, file editing, etc). We are aware than some
“basic” tools won’t work (less, emacs, etc). They won’t be fixed.

-  `Principle <docs/0_concepts.rst#principle>`__

   -  `How it works <docs/0_concepts.rst#how-it-works>`__

      -  `Bootstrap issue <docs/0_concepts.rst#bootstrap-issue>`__
      -  `About EPEL
         repository <docs/0_concepts.rst#about-epel-repository>`__
      -  `About links <docs/0_concepts.rst#about-links>`__
      -  `About dependencies <docs/0_concepts.rst#about-dependencies>`__
      -  `Dynamic libraries <docs/0_concepts.rst#dynamic-libraries>`__

   -  `Supported platforms <docs/0_concepts.rst#supported-platforms>`__

      -  `Trick <docs/0_concepts.rst#trick>`__

-  `Building RPMs <docs/10_RPMs.rst#building-rpms>`__

   -  `Patching the sources <docs/10_RPMs.rst#patching-the-sources>`__
   -  `Altering the normal build
      workflow <docs/10_RPMs.rst#altering-the-normal-build-workflow>`__
   -  `Caching mechanism <docs/10_RPMs.rst#caching-mechanism>`__
   -  `Adding an RPM package <docs/10_RPMs.rst#adding-an-rpm-package>`__

-  `Python packages <docs/20_pythonPackages.rst#python-packages>`__

   -  `Adding a python
      package <docs/20_pythonPackages.rst#adding-a-python-package>`__

-  `Generate a new
   diracos <docs/30_generatingDIRACOS.rst#generate-a-new-diracos>`__

   -  `Initial setup <docs/30_generatingDIRACOS.rst#initial-setup>`__
   -  `Configuration
      files <docs/30_generatingDIRACOS.rst#configuration-files>`__
   -  `Building
      everything <docs/30_generatingDIRACOS.rst#building-everything>`__
   -  `Build the python
      modules <docs/30_generatingDIRACOS.rst#build-the-python-modules>`__
   -  `Bundle DIRACOS <docs/30_generatingDIRACOS.rst#bundle-diracos>`__
   -  `Get your bundle <docs/30_generatingDIRACOS.rst#get-your-bundle>`__
   -  `Test it ! <docs/30_generatingDIRACOS.rst#test-it-!>`__

-  `Configuration Grammar <docs/40_grammar.rst#configuration-grammar>`__

   -  `rpmBuild section <docs/40_grammar.rst#rpmbuild-section>`__

      -  `Package and
         PackageGroup <docs/40_grammar.rst#package-and-packagegroup>`__

         -  `Mandatory
            parameters <docs/40_grammar.rst#mandatory-parameters>`__
         -  `Optional
            parameters <docs/40_grammar.rst#optional-parameters>`__

   -  `Other sections and
      options <docs/40_grammar.rst#other-sections-and-options>`__

-  `Troubleshoot <docs/50_troubleshoot.rst#troubleshoot>`__

   -  `Error
      `Requires: python(abi) = 2.6 <docs/50_troubleshoot.rst#error-requires-pythonabi-26>`__
   -  `Build is failing for broken rpm
      dependencies <docs/50_troubleshoot.rst#build-is-failing-for-broken-rpm-dependencies>`__
   -  `Script fails for missing python
      module <docs/50_troubleshoot.rst#script-fails-for-missing-python-module>`__
   -  `Symlinks <docs/50_troubleshoot.rst#symlinks>`__
   -  `Singularity <docs/50_troubleshoot.rst#singularity>`__
   -  `About
      manualDependencies <docs/50_troubleshoot.rst#about-manualdependencies>`__
   -  `LDD check failing <docs/50_troubleshoot.rst#ldd-check-failing>`__
   -  `ldconfig_scriptlets <docs/50_troubleshoot.rst#ldconfig_scriptlets>`__

-  `Test DIRACOS as a
   User <docs/60_useDIRACOS.rst#test-diracos-as-a-user>`__
-  `Make a new release <docs/70_release.rst#make-a-new-release>`__

   -  `Versioning <docs/70_release.rst#versioning>`__
   -  `Manual execution of
      steps <docs/70_release.rst#manual-execution-of-steps>`__

      -  `Get list of PRs and update release
         notes <docs/70_release.rst#get-list-of-prs-and-update-release-notes>`__
      -  `Make a release
         branch <docs/70_release.rst#make-a-release-branch>`__
      -  `Fix the pip requirements
         versions <docs/70_release.rst#fix-the-pip-requirements-versions>`__

         -  `About git
            packages <docs/70_release.rst#about-git-packages>`__

      -  `Build DIRACOS <docs/70_release.rst#build-diracos>`__
      -  `Deploy the archive <docs/70_release.rst#deploy-the-archive>`__

   -  `Automatic generation of a
      release <docs/70_release.rst#automatic-generation-of-a-release>`__

      -  `New Release <docs/70_release.rst#new-release>`__
      -  `Test Build <docs/70_release.rst#test-build>`__

-  `Extending DIRACOS <docs/80_extendingDIRACOS.rst#extending-diracos>`__

   -  `Requesting a package to be added in
      DIRACOS <docs/80_extendingDIRACOS.rst#requesting-a-package-to-be-added-in-diracos>`__
   -  `Adding pure python
      packages <docs/80_extendingDIRACOS.rst#adding-pure-python-packages>`__

      -  `Initial setup <docs/80_extendingDIRACOS.rst#initial-setup>`__
      -  `Configuration
         files <docs/80_extendingDIRACOS.rst#configuration-files>`__
      -  `Building the
         extension <docs/80_extendingDIRACOS.rst#building-the-extension>`__

   -  `Adding RPM packages or compiled python
      packages <docs/80_extendingDIRACOS.rst#adding-rpm-packages-or-compiled-python-packages>`__
   -  `Removing
      packages <docs/80_extendingDIRACOS.rst#removing-packages>`__
   -  `Using DIRACOS extension in your DIRAC
      extension <docs/80_extendingDIRACOS.rst#using-diracos-extension-in-your-dirac-extension>`__

Note: summary generated with

::

   # the pages are sorted thanks to the numbers in front
   for doc in $(find docs -type f -name '*.rst'| sort -n );
   do grep '^#' $doc | while read title;
      do
        # The text is the title, with an indentation level depending on the depth, with square brackets
        linkText=$(echo $title | sed -E -e 's/#{4}(.*)/      + [\1]/g' -e 's/#{3}(.*)/    + [\1]/g' -e 's/#{2}(.*)/  * [\1]/g' -e 's/#{1}(.*)/- [\1]/g')
        # The anchor is the title, all lowercase, without special char, with '-' instead of space
        anchor=$(echo $title | tr '[A-Z]' '[a-z]' |   sed -E -e 's/#+ +//g' -e 's/ /-/g');
        echo "$linkText($doc#$anchor)";
      done;
   done

Disclaimer
----------

DIRACOS is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. We are aiming at supporting SLC6 and
CC7, whilst we test also on other platforms we do not provide support
for those.

.. |pipeline status| image:: https://gitlab.cern.ch/CLICdp/iLCDirac/DIRACOS/badges/master/pipeline.svg
   :target: https://gitlab.cern.ch/CLICdp/iLCDirac/DIRACOS/pipelines
