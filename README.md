# Serverless Cloud Workshop

This repository is for learners on Corndel's DevOps apprenticeship.

There are two versions of this workshop:
* [Using Logic Apps](alternative_workshop.md)
  * This is recommended if you want to focus on working with Azure (and would prefer not to code at the same time)
* [Using Azure Functions](during_workshop.md)
  * This is recommended if you are comfortable with programming in Python (and/or want a refresher with general purpose coding)

## Pre-requisites

You should have received an email inviting you to the "Softwire Academy" Azure directory. Please accept the invitation if you haven't already - the username is of the form `first.last@softwireacademy.onmicrosoft.com`.

> If you have forgotten your password or lost your MFA device, a tutor can reset those for you.

Also, make sure you have installed the following:

* [Visual Studio Code](https://code.visualstudio.com/download)
* [Git](https://git-scm.com/)
* [Azure Functions Core Tools version 4.x.](https://docs.microsoft.com/en-gb/azure/azure-functions/functions-run-local#v2)
  * The Function Tools are not required if you are following the alternative exercise
  * :warning: At time of writing, Azure function tools for Python works with Python 3.6-3.9 on x86(/64) only, not on ARM for M1 Macs
    * [GitHub issue for M1 Macs](https://github.com/Azure/azure-functions-python-worker/issues/915)
    * [GitHub issue for Python3.10](https://github.com/Azure/azure-functions-python-worker/issues/899)
    * The workshop can also be done using [GitPod](https://gitpod.io/#https://github.com/CorndelWithSoftwire/DevOps-Course-Workshop-Module-08-Serverless)
* [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
* [Python](https://www.python.org/downloads/)
  * Version 3.6 or up; check this by running `python --version`
* [Postman](https://www.postman.com/downloads/)
