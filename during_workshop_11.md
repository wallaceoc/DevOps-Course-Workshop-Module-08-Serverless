# During the Workshop

Before starting make sure you have addressed the prerequisites in the [README.md](README.md)

AcmeSub are a company who create subtitles for films. They wish to automate the process of  translating their subtitles to the different languages they support. As this processing will take time, they are worried about how well the system will hold up when under heavy load. They have approached you to help them investigate the best infrastructure for this task.

## Part 1 - Load Testing

First of all we will investigate how well an application behaves under load when it is not *elastic* or *scalable*. For this exercise we will use a Python application that has one HTTP endpoint. This endpoint, see [/initialApp/app.py](/initialApp/app.py), will just wait for 5 seconds when it is called, this is to simulate the time it will take to do the actual processing that AcmeSub will require in the future.

  1. Navigate to the application's folder: `cd ./initialApp/` 
  2. Install requirements: `pip install -r requirements.txt`
  3. Run the app: `python -m flask run`

We will host this application in a non-scalable way, which we can then perform *load testing* against.
> The ideal demonstration of an outdated, non-scalable deployment would be via VMs, but these cost money, so for the purposes of this exercise we'll be using Azure App Service with scalability turned off, as this is available on the free service plan.

In the same folder as above:
 - Login to the Azure CLI: `az login`
 - Run the following command: `az webapp up --sku F1 --location ukwest --name <app-name>`
   - `<app-name>` should be replaced with a name that is unique across all of Azure (as this application will be hosted at `<app-name>.azurewebsites.net`). For example you could use your initials plus today's date e.g. `abc-01-01-1900-load-testing`.
 - The command should return the URL that the application is now hosted on. If you navigate to that URL in your browser it should take around 5 seconds before it loads with a message.

Now that we have the application running, we're going to use an online service, BlazeMeter, to perform load testing on it. With this tool we can send out a number of requests over a few minutes to see how the application performs.

  1. [Sign up for an account on the free tier of BlazeMeter](https://www.blazemeter.com/pricing/)
  2.  Create a new performance test by clicking 'Create Test' and then 'Performance Test':

  ![Create Test](/images/BlazeMeter/BlazeMeter-CreateTest.png)

  3. Choose 'Enter Url/API Call`

  ![Enter URL](/images/BlazeMeter/BlazeMeter-EnterUrl.png)

  4. Give the request any name you want, and then in the URL enter the URL of your application e.g. `http://abc-01-01-1900-load-testing.azurewebsites.net`

  ![URL For Request](/images/BlazeMeter/BlazeMeter-UrlEntered.png)

  5. Under 'Load Configuration' we can then set how many users will be used in this performance testing (i.e. how many clients will be requesting from the API simultaneously), how long the load test lasts for and how quickly users are added. Choose the following settings:
    - Total Users: 50
    - Duration: 5 minutes
    - Ramp up Time: 4 minutes
    - Ramp up Steps: 10

  ![Load Configuration](/images/BlazeMeter/BlazeMeter-LoadConfiguration.png) 

  6. The 'Load Configuration' lets you set where the requests will originate from. This doesn't matter too much to us, so just select one that is in the UK, as that is where our application is hosted.

  ![Load Distribution](/images/BlazeMeter/BlazeMeter-LoadDistribution.png) 

  7. Hit 'Run Test' on the left-hand side.

BlazeMeter will take a couple of minutes to warm up, before it then starts performing the load test on your application. Feel free to start looking at the next part whilst you wait for it to complete.

Once the test has booted up, it will redirect you to a summary screen, where you will be able to see information as the test is carried out, including average response time and number of errors.

When the test has ended you should hopefully see an average response time which is much higher than the 5 second wait that each request should have. This is because the application, on the current infrastructure, can only handle a limited number of requests at a time. Requests are ending up having to wait for the active requests to finish, and some may even be erroring due to them taking too long to respond.

If you go to the 'Timeline Report' tab you can select to see the average response time plotted against the number of users in the test. This should show that the response time got progressively worse as more users were added. Even when the users start to decrease the response time is still high as there is a backlog of requests that the server has to deal with.

![Response Time](/images/BlazeMeter/BlazeMeter-ResponseTimeGraph.png) 

## Part 2 - Azure Functions

To try and solve the problems that the application experiences under load we are going to convert our application to one that runs in a Serverless Environment, using Azure Functions.

### Step 1 - Running Locally

The first thing to do is to create a local function project. In Azure Functions, a function project is a container for one or more individual functions. To do this we will use Azure Functions Core Tools, that you installed in the prerequisites to this workshop.

```
func init AcmeSubProject --python
```

This will create a new folder called `AcmeSubProject`, which you will want to navigate into.

```
cd AcmeSubProject
```

Next, we want to create a function that will be triggered by an HTTP request, so we will use the 'HTTP trigger' template.

```
func new --name HttpEndpoint --template "HTTP trigger" --authlevel "anonymous"
```

This creates a new subfolder, containing the code for this function:

#### function.json

``` JSON
{
  "scriptFile": "__init__.py",
  "bindings": [
    {
      "authLevel": "Anonymous",
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "methods": [
        "get",
        "post"
      ]
    },
    {
      "type": "http",
      "direction": "out",
      "name": "$return"
    }
  ]
}
```

This is a configuration file that defines the *trigger* and *bindings* for the function.

*Triggers* are what causes a function to run, like an HTTP Request or a Timer. They have associated data, that can be passed into the function as a parameter. In the above instance the HTTP Trigger passes in its data as a parameter named `req`. Every Azure Function has exactly one trigger, with a trigger effectively being a special sort of *input binding*.

 A *binding* is how a function is connected to another resource and they can be either an *input binding* or an *output binding*. Input bindings receive data from a data source and pass it into the function as parameters. Output bindings take data from the function and send it to another resource, for example returning an HTTP response or creating a message in a Message Queue.

 Bindings prevent you from needing to hardcode access to other services within the function itself, they are declared in this JSON file. A function can have zero or many input and/or output bindings.

 The `scriptFile` property declares the name of the function that will be run.

 #### \_\_init\_\_.py

``` Python
import logging

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )

```

\_\_init\_\_.py contains a `main()` Python function, which is called when the function is triggered. It takes an HTTP Request as the parameter `req` and returns an HTTP Response, as per the configuration in *function.json*.

Before we worry about hosting the function on Azure itself we are going to test that in runs locally.

- Make sure you're in the root directory of the local function project (`AcmeSubProject`)
- Run command:  `func start`
- Towards the end of the output it should give you a URL. Copy this into a browser and append the query string `?name=<YOUR_NAME>` (so the full URL looks something like `http://localhost:7071/HttpEndpoint?name=Alice`)
- You should hopefully see a message returned from the function

Now that we have it running locally, we want to replace the code in the default function with something similar to the dummy code that we are using in our existing application. However, we will change it so we can send the text that we want to translate to it. Change \_\_init\_\_.py to look like the following:

``` Python
import time
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    start = time.time()

    req_body = req.get_json()
    subtitle = req_body.get("subtitle")

    time.sleep(5) # Simulating 5 seconds of cpu-intensive processing
    end = time.time()
    processingTime = end - start

    return func.HttpResponse(
        f"Processing took {str(processingTime)} seconds. Translation is: {subtitle}",
        status_code=200
    )

```

Once you've updated the code, you can run `func start` again to run the new version.

The function now expects us to send a JSON object to it containing the subtitle to translate, so instead of using the browser to test it, we will use Postman. Open up Postman and select to create a new request (File > New...). 
- Set the URL to the URL returned by `func start` command
- Under the 'Body' tab, select 'raw' and change the 'Text' dropdown to read 'JSON'
- In the textbox input the following JSON:
```
{
    "subtitle": "It was a bright cold day in April, and the clocks were striking thirteen."
}
- Hit 'Send'
```

![Postman](/images/Postman-SendRequest.png) 

### Step 2 - Hosting on Azure

Now that you've got your function working locally we're going to get it running on Azure.

Before the code can be deployed we need to create three resources in Azure, using the Azure CLI:

- A _Resource Group_: This is a container for related resources.

```
az group create --name AcmeSubResources --location ukwest
```

- A _Storage Account_: This is used to store the code for your functions, as well as to maintain state and other information about your project.

```
az storage account create --name <STORAGE_NAME> --location ukwest --resource-group AcmeSubResources --sku Standard_LRS
```
> (Replace `<STORAGE_NAME>` with the name you want to give this storage account, this must be unique across the whole of Azure Storage and contain 3 to 24 numbers or lowercase letters.)

- A _Function App_: This is the container for your function code within Azure, it can be thought of the Azure equivalent to your local function project.

```
az functionapp create --resource-group AcmeSubResources --consumption-plan-location ukwest --runtime python --runtime-version 3.8 --functions-version 3 --name <APP_NAME> --storage-account <STORAGE_NAME> --os-type linux
```

> `<STORAGE_NAME>` should be the name of the Storage Account you just created. Replace `<APP_NAME>` with a name that is unique across all of Azure (as this application will be hosted at `<APP_NAME>.azurewebsites.net`). For example you could use your initials plus today's date e.g. `abc-01-01-1900-functions`.

Now that we have all the resources that we need, we can deploy to Azure.

```
func azure functionapp publish <APP_NAME>
```
>Replace `<APP_NAME>` with the name you chose above for your Function App. Make sure you're in the root directory of the local function project (`AcmeSubProject`) when running the above command

As when running locally, the command should output a URL. You can use this URL in Postman to send a request to the function (don't forget to send the JSON object, as before!).

Now that you have your Azure Function setup, you can have a look at the resources you have created in the Azure Portal, by logging into https://portal.azure.com/ and selecting 'All Resources' from the menu in the top left corner.

### Step 3 - Load testing Azure Function

To test whether moving to a new cloud-based, elastic, serverless environment has improved performance when under load we should repeat the load testing we did with BlazeMeter, but this time using the URL for the Azure Function app you have just created. When setting the URL, you will also have to remember to pass in the JSON object your request is now expecting.

Hopefully, you should see three things:

- The average response time has been reduced. This is still higher than the 5 seconds that the function itself takes to run, this is due to there being an overhead as more instances of your function gets created, to handle the load.

- The response time does not increase dramatically when more users are added to the load test, as the Azure Functions is creating more instances of the function to handle the increased demand.

- There should (hopefully) be no errors, as there are no timeouts, as all requests are being handled in a timely manner.

## Part 3 - Integrating with Azure Table Storage

AcmeSub have been in touch, instead of processing the subtitles immediately, they would like us to instead save them to some storage that they can access later.

For the moment we want to just focus on the infrastructure, so we will keep using our function from Part 2, but we will alter it to save the subtitles somewhere.

### Step 1 - Setting up Azure Table Storage

For this exercise, we're going to use Azure Table storage, which is a NoSQL datastore.

```
az storage table create --name AcmeTranslations --account-name <STORAGE_NAME>
```
> We will use the same Storage Account that we created previously, so replace `<STORAGE_NAME>` with the name you used in Part 2 Step 2.

In the [Azure Portal](https://portal.azure.com/) you should now be able to find your created Table Storage:
- Search for 'Storage accounts' in the top search bar
- Select the storage account you are using for this workshop
- Select 'Storage Explorer'
- You should then be able to expand 'Tables' and select the table you just created
- For now it should show no data

### Step 2 - Binding to Azure Table Storage

We now want to change our function so it saves the subtitle to the Azure Storage table that has just been created. To do this you will need to:

1. Add a new binding definition to the _function.json_ file.
2. Change your Python function to use the new binding.
3. You can remove the `time.sleep(5)` line from your Python function at this point

It is worth checking out the [Table Storage output binding documentation](https://docs.microsoft.com/en-gb/azure/azure-functions/functions-bindings-storage-table-output?tabs=python) to help you achieve this task.

> As you are using the same Storage Account for your Azure Table Storage and for your Azure Functions App you do not need to set the `connection` property for the binding in _function.json_ as it will default to use the correct connection. 
To run the function locally you will need to run the command `func azure functionapp fetch-app-settings <app_name>` to make sure the local instance knows about the correct connection details.

You can check whether you have been successful by using the Azure Portal to see if your function is adding data to the Azure Table.

## Part 4 - Using Event Grid

AcmeSub need to be able to translate their subtitles into multiple different languages. One way we could architect this is to kick off an Azure function instance per language. To help us achieve this we are going to be using Azure Event Grid.

The way we want the application to work is:
1. Azure Function _A_ receives an HTTP Request containing the subtitle and the languages to translate the subtitle into.
2. Function _A_ saves the subtitle to Azure Table storage
3. Function _A_ sends out an _event_ per language, this event contains the location of the subtitle in Azure Table storage and the language to translate it to.
4. Function _B_ receives an event from Function A. It will use the information in the event to retrieve the subtitle from Azure Table Storage.
5. Function _B_ will process this subtitle, based on the language contained in the event.
6. Function _B_ will save the processed subtitle into a different table in Azure Table storage.

As you can see, our existing Azure Function acts very closely to how Function _A_ needs to behave, so we will tweak that one and then create a new function for Function _B_.

### Step 1 - Setup Event Grid

Azure Event Grid lets us _publish_ events to a _topic_. We can then _subscribe_ to a _topic_ to receive those events elsewhere.

We'll first of all create a topic in the existing resource group:

```
az eventgrid topic create --resource-group AcmeSubResources --name SubtitleAdded --location ukwest
```

To publish events to a topic we need to know the address of the topic endpoint and we must also have the key. You can get these by running the following commands:
```
az eventgrid topic show --name SubtitleAdded -g AcmeSubResources --query "endpoint"
```
```
az eventgrid topic key list --name SubtitleAdded -g AcmeSubResources --query "key1"
```

You now need to tell Azure Functions about these two values. In the root directory of your `AcmeSubProject` function app there will be a _local.settings.json_ file. You will want to add two new properties under the `Values` property containing these. That file should end up looking something like:

``` JSON
{
  "IsEncrypted": false,
  "Values": {
    "SubtitleAddedEndpoint": "<ENDPOINT>",
    "SubtitleAddedKey": "<KEY>",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    // OTHER VALUES
  },
  "ConnectionStrings": {}
}
```

Your functions will now have access to those values when running locally, however you'll need to publish the settings for them to be available when running your functions on Azure. To publish your settings run:

```
func azure functionapp publish <function-app-name> --publish-settings-only
```

### Step 2 - Sending events

We now want to change our existing _HttpEndpoint_ function to send events to the Event Grid topic. To do so you will need to:

1. Change the JSON that you send in the HTTP request to include the language codes for the subtitle to be translated to. For example:

``` JSON
{
    "subtitle": "It was a bright cold day in April, and the clocks were striking thirteen.",
    "languages": ["it", "de"]
}
```

2. 

## Part 5 (Optional) - Transcribing and Translating using a PaaS

## Part 6 (Optional) - Using Serverless framework
