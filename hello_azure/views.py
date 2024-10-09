from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.http import JsonResponse

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

import stripe
import os

def index(request):
    print('Request for index page received')
    return render(request, 'hello_azure/index.html')

def standalone_button(request):
    print('Payment')
    return render(request, 'hello_azure/standalone button.html')

def redirect_button (request):
    return render(request, 'hello_azure/redirect_button.html')


###
# needs to be hided.

key_vault_url = "https://exemplar-ai-prod.vault.azure.net/"
credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=key_vault_url, credential=credential)

stripe_key_string = ''
secret_stripe_key_string = 'stripe-api-key'   # Currently using chaesang's private one.
try:
    # Retrieve the secret
    retrieved_stripe_key_string = secret_client.get_secret(secret_stripe_key_string)
    stripe_key_string = retrieved_stripe_key_string.value  # Ensure value is assigned here
except Exception as e:
    print("Error retrieving secret:", str(e))

stripe.api_key = stripe_key_string

@csrf_exempt
def hello(request):
    ###
    # Testing for getting key vault
    ###

    print('----- Before setting')

    # Replace with your Key Vault URL
    key_vault_url = "https://exemplar-test-value.vault.azure.net/"

    print('----- Before DefaultAzureCredential')

    # Initialize the DefaultAzureCredential (uses environment variables or managed identity)
    credential = DefaultAzureCredential()

    print('----- Before SecretClient')

    # Create a SecretClient using the URL and credentials
    secret_client = SecretClient(vault_url=key_vault_url, credential=credential)

    # Replace with your secret name
    secret_name = "exemplar-test-key"

    print('----- Before get_secret')

    try:
    # Retrieve the secret
        retrieved_secret = secret_client.get_secret(secret_name)
    except Exception as e:
        print("Error retrieving secret:", str(e))
        # Handle the error, e.g., log it, retry, or raise a custom exception
    
    print('----- After get_secret')

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
    
@csrf_exempt
def create_checkout_session(request):
    # You need to manually switch the domain URL
    # domain_url='http://localhost:8000'
    domain_url='https://helloworld-exemplar-django.azurewebsites.net'

    id = request.POST.get('product')
    amount = 0

    if id == 'Product1':
        amount = 1000
    elif id == 'Prouct2':
        amount = 2000
    elif id == 'Product3':
        amount = 5000
    elif id == 'Dynamic':
        amount = int(request.POST.get('number'))*100

    if amount != 0:
        session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Points',
                        },
                        'unit_amount': amount,
                    },
                    'quantity': 1,
                }
            ],
            mode='payment',

            success_url=domain_url + '/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=domain_url + '/cancel',
            
        )

        return redirect(session.url, code=303)
    
    no_product = {
        "status": "success",
        "message": "No products are selected.",
    }
    return JsonResponse(no_product)

# http://localhost:3000/success?session_id=cs_test_a1mfCVlZiJuQ5OKR1JFIoafDHR19DEGD2M3GSiArUfT1v2fhDXH2xZHKN6
def success(request):
    print(stripe.api_key)
    id = request.GET.get('session_id')
    checkout_session = stripe.checkout.Session.retrieve(id)
    return JsonResponse(checkout_session)


def cancel(request):
    sample_data = {
        "status": "canceled",
        "message": "This is a sample JSON response with a canceled status.",
    }
    return JsonResponse(sample_data)
