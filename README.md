# Workshop Module 11

This repository is for learners on Corndel's DevOps apprenticeship.

During workshop 11 you'll be following the instructions in [during_workshop_11.md](during_workshop_11.md).

## Pre-requisites

You need to have an Azure account. You can create a free account [here](https://azure.microsoft.com/en-us/free/?WT.mc_id=A261C142F).

Also, make sure you have installed the following:

* [Visual Studio Code](https://code.visualstudio.com/download)
* [Git](https://git-scm.com/)



## Local installation of the app
  1. Install requirements: `pip install -r requirements.txt`
  2. Run the app: `python -m flask run`

## Deploy code:
> The ideal demonstration of an outdated non-scalable deployment would be via VMs, but these cost money, so for the purposes of this exercise we'll be using the approximation of an Azure WebApp deployment without any additional features.

 - Run the following command: `az webapp up --sku F1 --location <location> --name <app-name>`