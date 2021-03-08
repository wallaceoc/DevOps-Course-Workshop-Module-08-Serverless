# During the Workshop

Before starting make sure you have addressed the prerequisites in the [README.md](README.md)

AcmeSub are a company who create subtitles for films. They wish to automate the process of transcribing audio and translating it to the different languages they support. As this processing will take time, they are worried about how well the system will hold up when under heavy load. They have approached you to help them investigate the best infrastructure for this task.

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

### Step 1

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

 A *binding* is how functions are connected to other resources and can be either an *input binding* or an *output binding*. Input bindings receive data from a data source, and pass it into the function as parameters. Output bindings take data from the function and send it to another resource, for example returning an HTTP request or creating a message in a Queue.

 Bindings prevent you from needing to hardcode access to other services within the function itself, they are declared in this JSON file.

 The `scriptFile` property declares the name of the function that will be run.

 #### __init__.py