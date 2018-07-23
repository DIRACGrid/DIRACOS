# Test DIRACOS as a User


If you want to test DIRACOS in a DIRAC installation, it is enough to do the following:

```
  https://raw.githubusercontent.com/DIRACGrid/DIRAC/integration/Core/scripts/dirac-install.py
  chmod +x dirac-install.py
  ./dirac-install.py -r v6r20 --dirac-os --dirac-os-version=0.0.5
```
If you want to install it together with your extension, you will most probably have to copy the diracos tar files from `http://lhcbproject.web.cern.ch/lhcbproject/dist/Dirac_project/installSource/` to your own baseURL
