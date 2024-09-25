from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def index(request):
    print('Request for index page received')
    return render(request, 'hello_azure/index.html')

@csrf_exempt
def hello(request):
    ###
    # Testing for getting key vault
    ###
    
    # Replace with your Key Vault URL
    key_vault_url = "https://exemplar-test-value.vault.azure.net/"

    # Initialize the DefaultAzureCredential (uses environment variables or managed identity)
    credential = DefaultAzureCredential()

    # Create a SecretClient using the URL and credentials
    secret_client = SecretClient(vault_url=key_vault_url, credential=credential)

    # Replace with your secret name
    secret_name = "exemplar-test-key"

    # Retrieve the secret
    retrieved_secret = secret_client.get_secret(secret_name)
    secret_value = retrieved_secret.value

    # Print the secret value
    print(f"Secret value: {secret_value}")

    print('----- hello ----- ')


    if request.method == 'POST':
        name = request.POST.get('name')
        
        if name is None or name == '':
            print("Request for hello page received with no name or blank name -- redirecting")
            return redirect('index')
        else:
            print("Request for hello page received with name=%s" % name)
            context = {'name': name + ' ' + secret_value }
            return render(request, 'hello_azure/hello.html', context)
    else:
        return redirect('index')